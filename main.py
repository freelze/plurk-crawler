import asyncio
import os
import sys
import time
from dotenv import load_dotenv
from plurk_oauth import PlurkAPI
from plurk_crawler import process_user

# Load Environment Variables
load_dotenv()

consumer_key = os.getenv("CONSUMER_KEY")
consumer_secret = os.getenv("CONSUMER_SECRET")
access_token = os.getenv("ACCESS_TOKEN")
access_token_secret = os.getenv("ACCESS_TOKEN_SECRET")

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
