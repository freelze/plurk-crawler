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

load_dotenv()

CONSUMER_KEY = os.getenv("CONSUMER_KEY")
CONSUMER_SECRET = os.getenv("CONSUMER_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")

url_validation_regex = re.compile(
    r'^(?:http|ftp)s?://' 
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' 
    r'localhost|' 
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' 
    r'(?::\d+)?' 
    r'(?:/?|[/?]\S+)$', re.IGNORECASE)

async def urlExists(session, path):
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
              
async def getPublicPlurks(plurk, _id, time_Offset):
    try:
        rawJson = await asyncio.to_thread(partial(plurk.callAPI,
                                                  '/APP/Timeline/getPublicPlurks',
                                                  {'user_id': _id, 'offset': time_Offset, 'limit': 30,
                                                   'favorers_detail': False, 'limited_detail': False, 'replurkers_detail': False}))
        return rawJson['plurks']
    except Exception as e:
        print(f"An error occurred while fetching public plurks: {e}")
        return []

async def parsePostsJob(plurk, i, owner_id, userName, lowStandardFav):
    image_path = f'./{userName}/'
    thisPostMediaCount = 0
    async with aiohttp.ClientSession() as session:
        if i['owner_id'] != owner_id:
            return

        if i['favorite_count'] > lowStandardFav:
            await getResponsesJob(plurk, session, i['plurk_id'], owner_id, userName)

        owner_id_str = str(owner_id)
        base36_plurk_id = str(base36.dumps(i['plurk_id']))

        splitStr = i['posted'].split()
        abbr_to_num = {name: num for num, name in enumerate(calendar.month_abbr) if num}
        fileNameTime = splitStr[3] + '_' + str(abbr_to_num[splitStr[2]]) + '_' + splitStr[1]

        _list = i['content'].split()
        tasks = []
        for content in _list:
            if content.startswith('href'):
                content = content[:-1]
                supported_format = ['jpg', 'png', 'gif', 'mp4', 'webp', 'bmp', 'svg']
                if content[-3:] in supported_format:
                    if re.match(url_validation_regex, str(content[6:])) is None:
                        continue
                    if not await urlExists(session, str(content[6:])):
                        continue
                    thisPostMediaCount += 1
                    imageNameWithoutPath = f"{fileNameTime}-plurk-{base36_plurk_id}-{thisPostMediaCount}-{owner_id_str}.{content[-3:]}"
                    image_name = image_path + imageNameWithoutPath
                    if os.path.isfile(image_name):
                        print(f"[✗] {imageNameWithoutPath} was already downloaded.")
                        continue
                    print(f'[✓] downloading {imageNameWithoutPath}')
                    tasks.append(download_image(session, str(content[6:]), image_name))
        await asyncio.gather(*tasks)
            
async def getResponses(plurk, pID):
    try:
        rawJson = await asyncio.to_thread(partial(plurk.callAPI,
                                                  '/APP/Responses/get',
                                                  {'plurk_id': pID}))
        return rawJson
    except Exception as e:
        print(f"An error occurred while fetching responses: {e}")
        return {}

async def getResponsesJob(plurk, session, pID, owner_id, userName):
    owner_id_str = str(owner_id)
    image_path = f'./{userName}/'
    base36_plurk_id = str(base36.dumps(pID))
    res_raw_json = await getResponses(plurk, pID)
    response_count = 0
    thisPostMediaCount = 0

    tasks = []
    for j in res_raw_json['responses']:
        response_count += 1
        if j['user_id'] == owner_id:
            splitStr = j['posted'].split()
            abbr_to_num = {name: num for num, name in enumerate(calendar.month_abbr) if num}
            fileNameTime = splitStr[3] + '_' + str(abbr_to_num[splitStr[2]]) + '_' + splitStr[1]
            content_str = j['content']
            match = re.findall(r"href=\S+", content_str)
            matchList = []
            for matchCase in match:
                matchCase = matchCase[:-1]
                matchCase = matchCase[6:]
                matchList.append(matchCase)
            for responseLink in matchList:
                supported_format = ['jpg', 'png', 'gif', 'mp4', 'webp', 'bmp', 'svg']
                if responseLink[-3:] in supported_format:
                    if re.match(url_validation_regex, responseLink) is None:
                        print(f"Invalid URL: {responseLink}")
                        continue
                    if not await urlExists(session, responseLink):
                        print(f"URL does not exist: {responseLink}")
                        continue
                    thisPostMediaCount += 1
                    imageNameWithoutPath = f"{fileNameTime}-plurk-{base36_plurk_id}-{thisPostMediaCount}-response-{response_count}-{owner_id_str}.{responseLink[-3:]}"
                    image_name = image_path + imageNameWithoutPath
                    if os.path.isfile(image_name):
                        print(f"[✗] {imageNameWithoutPath} was already downloaded.")
                        continue
                    print(f'[✓] downloading {imageNameWithoutPath}')
                    tasks.append(download_image(session, responseLink, image_name))
    await asyncio.gather(*tasks)
                        
async def getPublicPlurks(plurk, _id, time_Offset, limit=30):
    try:
        rawJson = await asyncio.to_thread(partial(plurk.callAPI,
                                                  '/APP/Timeline/getPublicPlurks',
                                                  {'user_id': _id, 'offset': time_Offset, 'limit': limit,
                                                   'favorers_detail': False, 'limited_detail': False, 'replurkers_detail': False}))
        return rawJson['plurks']
    except Exception as e:
        print(f"An error occurred while fetching public plurks: {e}")
        return []
        
async def process_user(plurk, user_name):
    public_profile = plurk.callAPI('/APP/Profile/getPublicProfile', {'user_id': user_name})
    if public_profile is None:
        print(f'User {user_name} Not Found!')
        return

    user_id = public_profile['user_info']['id']
    path = f'./{user_name}'
    
    if not os.path.exists(path):
        os.mkdir(path)
    timeOffset = strftime("%Y-%m-%dT%H:%M:%S", gmtime())

    # store json_data
    json_data_queue = asyncio.Queue()

    async def producer():
        nonlocal timeOffset
        while True:
            json_data = await getPublicPlurks(plurk, user_id, timeOffset)
            if len(json_data) == 0:
                await json_data_queue.put(None) 
                break
            await json_data_queue.put(json_data)
            splitStr = json_data[-1]['posted'].split()
            abbr_to_num = {name: num for num, name in enumerate(calendar.month_abbr) if num}
            timeOffset = f"{splitStr[3]}-{abbr_to_num[splitStr[2]]}-{splitStr[1]}T{splitStr[4]}"

    async def consumer():
        lowStandardFav = -1
        async with aiomultiprocess.Pool() as pool:
            while True:
                json_data = await json_data_queue.get()
                if json_data is None:  
                    break
                tasks = [pool.apply(parsePostsJob, (plurk, i, user_id, user_name, lowStandardFav)) for i in json_data]
                await asyncio.gather(*tasks)

    producer_task = asyncio.create_task(producer())
    await consumer()
            
async def main():
    plurk = PlurkAPI(CONSUMER_KEY, CONSUMER_SECRET)
    plurk.authorize(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)

    if len(sys.argv) == 1:
        userNamesList = input("Please enter at least one username OR several usernames with space separated:")
        userNamesList = userNamesList.split()
    else:
        userNamesList = sys.argv[1:]
    async with aiomultiprocess.Pool() as pool:
        await asyncio.gather(*[process_user(plurk, user_name) for user_name in userNamesList])
  
if __name__ == "__main__":
    t1 = time.time()
    asyncio.run(main())
    print("============================\nTotal time: {}\n".format(time.time() - t1))