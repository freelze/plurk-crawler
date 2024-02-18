import aiohttp
import aiomultiprocess
import asyncio
import base36
import calendar
import os
import re
import sys
import time
from dotenv import load_dotenv
from functools import partial
from plurk_oauth import PlurkAPI
from time import gmtime, strftime

# Load Environment Variables
load_dotenv()

consumer_key = os.getenv("CONSUMER_KEY")
consumer_secret = os.getenv("CONSUMER_SECRET")
access_token = os.getenv("ACCESS_TOKEN")
access_token_secret = os.getenv("ACCESS_TOKEN_SECRET")

url_validation_pattern = re.compile(
    r'^(?:http|ftp)s?://'
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' 
    r'localhost|'
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' 
    r'(?::\d+)?' 
    r'(?:/?|[/?]\S+)$', re.IGNORECASE)

async def url_exists(session, path):
    try:
        async with session.head(path, allow_redirects=True, timeout=10) as response:
            return response.status == 200
    except Exception as e:
        print(f"Error checking URL: {e}")
        return False

async def download_image(session, image_url, image_name):
    async with session.get(image_url) as response:
        with open(image_name, 'wb') as handler:
            handler.write(await response.read())  

async def get_public_plurks(plurk, _id, time_offset, limit=30):
    try:
        raw_json = await asyncio.to_thread(
            partial(
                plurk.callAPI,
                '/APP/Timeline/getPublicPlurks',
                {
                    'user_id': _id,
                    'offset': time_offset,
                    'limit': limit,
                    'favorers_detail': False,
                    'limited_detail': False,
                    'replurkers_detail': False
                }
            )
        )
        return raw_json['plurks']
    except Exception as e:
        print(f"An error occurred while fetching public plurks: {e}")
        return []
    
async def get_responses(plurk, p_id):
    try:
        raw_json = await asyncio.to_thread(
            partial(
                plurk.callAPI,
                '/APP/Responses/get',
                {
                    'plurk_id': p_id
                }
            )
        )
        return raw_json
    except Exception as e:
        print(f"An error occurred while fetching responses: {e}")
        return {}

async def parse_posts_job(plurk, post, owner_id, user_name, low_standard_fav):
    image_path = f'./{user_name}/'
    plurk_media_num = 0
    content_media_num = 0
    async with aiohttp.ClientSession() as session:
        # if the post is replurk then skip
        if post['owner_id'] != owner_id:
            return

        if post['favorite_count'] > low_standard_fav:
            await download_response_media(plurk, session, post['plurk_id'], owner_id, user_name)

        owner_id_str = str(owner_id)
        base36_plurk_id = str(base36.dumps(post['plurk_id']))

        split_str = post['posted'].split()
        abbr_to_num = {name: num for num, name in enumerate(calendar.month_abbr) if num}
        file_name_time = split_str[3] + '_' + str(abbr_to_num[split_str[2]]) + '_' + split_str[1]

        content_list = post['content'].split()
        tasks = []
        # Loop through every content in the post
        for content in content_list:
            if content.startswith('href'):
                content = content[:-1]
                supported_format = ['jpg', 'png', 'gif', 'mp4', 'webp', 'bmp', 'svg']
                if content[-3:] in supported_format:
                    if re.match(url_validation_pattern, str(content[6:])) is None:
                        continue
                    if not await url_exists(session, str(content[6:])):
                        continue
                    plurk_media_num += 1
                    content_media_num += 1
                    image_name_without_path = f"{file_name_time}-plurk-{base36_plurk_id}-{plurk_media_num}-content_media_num-{content_media_num}-{owner_id_str}.{content[-3:]}"
                    image_name = image_path + image_name_without_path
                    if os.path.isfile(image_name):
                        print(f"[✗] {image_name_without_path} was already downloaded.")
                        continue
                    print(f'[✓] downloading {image_name_without_path}')
                    tasks.append(download_image(session, str(content[6:]), image_name))
        await asyncio.gather(*tasks)

async def download_response_media(plurk, session, p_id, owner_id, user_name):
    owner_id_str = str(owner_id)
    image_path = f'./{user_name}/'
    base36_plurk_id = str(base36.dumps(p_id))
    res_raw_json = await get_responses(plurk, p_id)
    response_num = 0
    plurk_media_num = 0

    tasks = []
    # Loop through every response
    for response_post in res_raw_json['responses']:
        response_num += 1
        # Check if the response is from the owner itself
        if response_post['user_id'] == owner_id:
            split_str = response_post['posted'].split()
            abbr_to_num = {name: num for num, name in enumerate(calendar.month_abbr) if num}
            file_name_time = split_str[3] + '_' + str(abbr_to_num[split_str[2]]) + '_' + split_str[1]
            content_str = response_post['content']
            match = re.findall(r"href=\S+", content_str)
            match_list = []
            for match_case in match:
                match_case = match_case[:-1]
                match_case = match_case[6:]
                match_list.append(match_case)
            for response_link in match_list:
                supported_format = ['jpg', 'png', 'gif', 'mp4', 'webp', 'bmp', 'svg']
                if response_link[-3:] in supported_format:
                    if re.match(url_validation_pattern, response_link) is None:
                        print(f"Invalid URL: {response_link}")
                        continue
                    if not await url_exists(session, response_link):
                        print(f"URL does not exist: {response_link}")
                        continue
                    plurk_media_num += 1
                    image_name_without_path = f"{file_name_time}-plurk-{base36_plurk_id}-{plurk_media_num}-response-{response_num}-{owner_id_str}.{response_link[-3:]}"
                    image_name = image_path + image_name_without_path
                    if os.path.isfile(image_name):
                        print(f"[✗] {image_name_without_path} was already downloaded.")
                        continue
                    print(f'[✓] downloading {image_name_without_path}')
                    tasks.append(download_image(session, response_link, image_name))
    await asyncio.gather(*tasks)


async def process_user(plurk, user_name):
    public_profile = plurk.callAPI('/APP/Profile/getPublicProfile', {'user_id': user_name})
    if public_profile is None:
        print(f'User {user_name} Not Found!')
        return

    user_id = public_profile['user_info']['id']
    path = f'./{user_name}'

    if not os.path.exists(path):
        os.mkdir(path)
    time_offset = strftime("%Y-%m-%dT%H:%M:%S", gmtime())

    json_data_queue = asyncio.Queue()

    async def producer():
        nonlocal time_offset
        while True:
            json_data = await get_public_plurks(plurk, user_id, time_offset)
            if len(json_data) == 0:
                await json_data_queue.put(None) 
                break
            await json_data_queue.put(json_data)
            split_str = json_data[-1]['posted'].split()
            abbr_to_num = {name: num for num, name in enumerate(calendar.month_abbr) if num}
            time_offset = f"{split_str[3]}-{abbr_to_num[split_str[2]]}-{split_str[1]}T{split_str[4]}"

    async def consumer():
        low_standard_fav = -1
        async with aiomultiprocess.Pool() as pool:
            while True:
                json_data = await json_data_queue.get()
                if json_data is None:  
                    break
                tasks = [pool.apply(parse_posts_job, (plurk, i, user_id, user_name, low_standard_fav)) for i in json_data]
                await asyncio.gather(*tasks)

    asyncio.create_task(producer())
    await consumer()
            
async def main():
    plurk = PlurkAPI(consumer_key, consumer_secret)
    plurk.authorize(access_token, access_token_secret)

    if len(sys.argv) == 1:
        user_names_list = input("Please enter at least one username OR several usernames with space separated:")
        user_names_list = user_names_list.split()
    else:
        user_names_list = sys.argv[1:]
    #async with aiomultiprocess.Pool() as pool:
    await asyncio.gather(*[process_user(plurk, user_name) for user_name in user_names_list])
  
if __name__ == "__main__":
    t1 = time.time()
    asyncio.run(main())
    print("============================\nTotal time: {}\n".format(time.time() - t1))
