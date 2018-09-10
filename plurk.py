#!/usr/bin/python
# -*- coding:utf-8 -*-

# ref: https://github.com/clsung/plurk-oauth 
# You can retrieve your app keys via the test tool at http://www.plurk.com/PlurkApp/
CONSUMER_KEY = ''
CONSUMER_SECRET = ''
ACCESS_TOKEN = ''
ACCESS_TOKEN_SECRET = ''

#mainUserName = ''

from plurk_oauth import PlurkAPI
import multiprocessing as mp
from multiprocessing import Pool
import re
import json
import os
import requests
import calendar
import time
from time import gmtime, strftime
# https://stackoverflow.com/questions/1181919/python-base-36-encoding 
import base36
import sys
#from pprint import pprint

# ref: https://stackoverflow.com/questions/7160737/python-how-to-validate-a-url-in-python-malformed-or-not
url_validation_regex = re.compile(
        r'^(?:http|ftp)s?://' # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
        r'localhost|' #localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?' # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)

# ref: https://stackoverflow.com/questions/16511337/correct-way-to-try-except-using-python-requests-module
def urlExists(path):
	try:
		r = requests.get(path,timeout=10)
		#print('r =',r)
	except requests.exceptions.RequestException as err:
		print("OOps: Something Else",err)
		return False
	except requests.exceptions.HTTPError as errh:
		print ("Http Error:",errh)
		return False
	except requests.exceptions.ConnectionError as errc:
		print ("Error Connecting:",errc)
		return False
	except requests.exceptions.Timeout as errt:
		print ("Timeout Error:",errt)    
		return False
	else:
		return r.status_code == requests.codes.ok

def getPublicPlurks( _plurk, _id, time_Offset ):
	rawJson = _plurk.callAPI('/APP/Timeline/getPublicPlurks',{'user_id':_id, 'offset':time_Offset, 'limit':30, 'favorers_detail':False, 'limited_detail':False, 'replurkers_detail':False})['plurks']
	return rawJson

def plurkApiLogin():
	_plurk = PlurkAPI(CONSUMER_KEY, CONSUMER_SECRET)
	_plurk.authorize(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
	checkToken = _plurk.callAPI('/APP/checkToken')
	if (checkToken is None):
		print("Your CONSUMER_KEY or CONSUMER_SECRET is wrong!")
		time.sleep(1)
		raise SystemExit
		exit()
	return _plurk
	
def parsePostsJob(i):

	#basePath = os.getcwd() + '\\'
	#basePath = os.getcwd() + '\\' + userName + '\\'
	baseUrl = "https://www.plurk.com/p/"
	image_path = './{}/'.format(userName)
	#path = './' + userName
	
	thisPostMediaCount = 0
		
	#print(i['plurk_id'])

	if (i['owner_id'] != id):
		#print(type(i['owner_id']))
		#print(type(id))
		#print("posted:", i['posted'])
		#print("i['owner_id']:",i['owner_id'])
		#print("@@@@@@@@@@replurk@@@@@@@@@@")
		return
	if (i['favorite_count'] > lowStandardFav):
		#parsePostsJob.q.put(i['plurk_id']) # store count of posts
		#print("===================================================================================")		
		"""
		old_stdout = sys.stdout
		log_file = open("parsePostsJob.log","a")
		sys.stdout = log_file
		
		sys.stdout = old_stdout
		log_file.close()
		"""
		#print("plurk_id =",i['plurk_id'])
		
		# get Response images
		getResponsesJob(i['plurk_id'])
		
		owner_id_int = i['owner_id']
		owner_id = str(i['owner_id'])
		#print("owner_id:", i['owner_id'])
		base36_plurk_id = str(base36.dumps(i['plurk_id']))
		#print("postUrl:", baseUrl + base36_plurk_id)
		#print("posted:", i['posted'])

		splitStr = i['posted'].split()
		abbr_to_num = {name: num for num, name in enumerate(calendar.month_abbr) if num}
		fileNameTime = splitStr[3] + '_' + str(abbr_to_num[splitStr[2]]) + '_' + splitStr[1]
		#print("******************")
		#print("porn:", i['porn'])
		#print("favorite_count:", i['favorite_count'])
		#print("response_count:", i['response_count'])
		#pprint(i['content_raw'])  # type:str

		#parsePostsJob.q.put(i['plurk_id'])

		# parse main plurk
		_list = i['content'].split()
		for content in _list:
			if (content[0:4] == 'href'):
				content = content[:-1]
				if (content[-3:] == 'jpg'):
					if (re.match(url_validation_regex, str(content[6:])) is None):
						#print("FALSE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
						continue
					if (urlExists(str(content[6:])) == False):
						#print("FALSE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
						continue
					#print(content[6:])
					thisPostMediaCount += 1
					imageNameWithoutPath = "{0}-plurk-{1}-{2}-{3}.jpg".format( fileNameTime, base36_plurk_id, str(thisPostMediaCount), owner_id )
					image_name = image_path + imageNameWithoutPath
					#image_name = fileNameTime + '-' + base36_plurk_id + '-' + str(
						#thisPostMediaCount) + '-' + owner_id + ".jpg"
					#path = basePath + image_name
					if (os.path.isfile(image_name)):
						print( "[✗] {} was already downloaded.".format(imageNameWithoutPath))
						continue
					print('[✓] donwloading {}'.format(imageNameWithoutPath))
					with open(image_name, 'wb') as handler:
						handler.write(requests.get(str(content[6:])).content)
				elif (content[-3:] == 'png'):
					if (re.match(url_validation_regex, str(content[6:])) is None):
						#print("FALSE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
						continue
					if (urlExists(str(content[6:])) == False):
						#print("FALSE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
						continue
					#print(content[6:])
					thisPostMediaCount += 1
					imageNameWithoutPath = "{0}-plurk-{1}-{2}-{3}.png".format( fileNameTime, base36_plurk_id, str(thisPostMediaCount), owner_id )
					image_name = image_path + imageNameWithoutPath
					#image_name = fileNameTime + '-' + base36_plurk_id + '-' + str(
						#thisPostMediaCount) + '-' + owner_id + ".png"
					#path = basePath + image_name
					if (os.path.isfile(image_name)):
						print( "[✗] {} was already downloaded.".format(imageNameWithoutPath))
						continue
					print('[✓] donwloading {}'.format(imageNameWithoutPath))
					with open(image_name, 'wb') as handler:
						handler.write(requests.get(str(content[6:])).content)
				elif (content[-3:] == 'gif'):
					if (re.match(url_validation_regex, str(content[6:])) is None):
						#print("FALSE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
						continue
					if (urlExists(str(content[6:])) == False):
						#print("FALSE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
						continue
					#print(content[6:])
					thisPostMediaCount += 1
					imageNameWithoutPath = "{0}-plurk-{1}-{2}-{3}.gif".format( fileNameTime, base36_plurk_id, str(thisPostMediaCount), owner_id )
					image_name = image_path + imageNameWithoutPath
					#image_name = fileNameTime + '-' + base36_plurk_id + '-' + str(
						#thisPostMediaCount) + '-' + owner_id + ".gif"
					#path = basePath + image_name
					if (os.path.isfile(image_name)):
						print( "[✗] {} was already downloaded.".format(imageNameWithoutPath))
						continue
					print('[✓] donwloading {}'.format(imageNameWithoutPath))
					with open(image_name, 'wb') as handler:
						handler.write(requests.get(str(content[6:])).content)
				elif (content[-3:] == 'mp4'):
					if (re.match(url_validation_regex, str(content[6:])) is None):
						print("FALSE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
						continue
					if (urlExists(str(content[6:])) == False):
						print("FALSE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
						continue
					print(content[6:])
					thisPostMediaCount += 1
					imageNameWithoutPath = "{0}-plurk-{1}-{2}-{3}.mp4".format( fileNameTime, base36_plurk_id, str(thisPostMediaCount), owner_id )
					image_name = image_path + imageNameWithoutPath
					#image_name = fileNameTime + '-' + base36_plurk_id + '-' + str(
						#thisPostMediaCount) + '-' + owner_id + ".mp4"
					#path = basePath + image_name
					if (os.path.isfile(image_name)):
						print( "[✗] {} was already downloaded.".format(imageNameWithoutPath))
						continue
					print('[✓] donwloading {}'.format(imageNameWithoutPath))	
					with open(image_name, 'wb') as handler:
						handler.write(requests.get(str(content[6:])).content)
				#else:
					#print("others link:", content[6:])
		
		#return i['plurk_id']
		#return
def getResponsesJob(pID):
	"""
	old_stdout = sys.stdout
	log_file = open("getResponsesJob.log","a")
	sys.stdout = log_file
	print(pID) 
	sys.stdout = old_stdout
	log_file.close()
	"""
	owner_id = str(id)
	res_raw_json = plurk.callAPI('/APP/Responses/get', {'plurk_id':pID} )
	#basePath = os.getcwd() + '\\'
	image_path = './{}/'.format(userName)
	base36_plurk_id = str(base36.dumps(pID))

	# for loop each responses
	#response_media = 0
	response_count = 0
	thisPostMediaCount = 0
	
	for j in res_raw_json['responses']:
		response_count += 1
		if (j['user_id'] == id):
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
				if (responseLink[-4:] == '.jpg'):
					if (re.match(url_validation_regex, responseLink) is None):
						#print("FALSE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
						continue
					if (urlExists(responseLink) == False):
						#print("FALSE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
						continue
					
					#response_count += 1
					thisPostMediaCount += 1
					imageNameWithoutPath = "{0}-plurk-{1}-{2}-response-{3}-{4}.jpg".format( fileNameTime, base36_plurk_id, str(thisPostMediaCount), str(response_count), owner_id )
					#imageNameWithoutPath = "{0}-plurk-{1}-response-{2}-{3}.jpg".format( fileNameTime, base36_plurk_id, str(response_count), owner_id )
					image_name = image_path + imageNameWithoutPath
					#image_name = fileNameTime + '-' + base36_plurk_id + '-' + str(
						#thisPostMediaCount) + '-' + "response" + '-' + str(
						#response_count) + '-' + owner_id + ".jpg"
					#path = basePath + image_name
					if (os.path.isfile(image_name)):
						print( "[✗] {} was already downloaded.".format(imageNameWithoutPath))
						continue
					print('[✓] donwloading {}'.format(imageNameWithoutPath))
					with open(image_name, 'wb') as handler:
						handler.write(requests.get(str(responseLink)).content)
				elif (responseLink[-4:] == '.png'):
					if (re.match(url_validation_regex, responseLink) is None):
						#print("FALSE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
						continue
					if (urlExists(responseLink) == False):
						#print("FALSE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
						continue
					
					#response_count += 1
					
					thisPostMediaCount += 1
					imageNameWithoutPath = "{0}-plurk-{1}-{2}-response-{3}-{4}.png".format( fileNameTime, base36_plurk_id, str(thisPostMediaCount), str(response_count), owner_id )
					#imageNameWithoutPath = "{0}-plurk-{1}-response-{2}-{3}.jpg".format( fileNameTime, base36_plurk_id, str(response_count), owner_id )
					image_name = image_path + imageNameWithoutPath
					#image_name = fileNameTime + '-' + base36_plurk_id + '-' + str(
						#thisPostMediaCount) + '-' + "response" + '-' + str(
						#response_count) + '-' + owner_id + ".png"
					#path = basePath + image_name
					if (os.path.isfile(image_name)):
						print( "[✗] {} was already downloaded.".format(imageNameWithoutPath))
						continue
					print('[✓] donwloading {}'.format(imageNameWithoutPath))
					with open(image_name, 'wb') as handler:
						handler.write(requests.get(str(responseLink)).content)
				elif (responseLink[-4:] == '.gif'):
					if (re.match(url_validation_regex, responseLink) is None):
						#print("FALSE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
						continue
					if (urlExists(responseLink) == False):
						#print("FALSE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
						continue
					
					#response_count += 1
					
					thisPostMediaCount += 1
					imageNameWithoutPath = "{0}-plurk-{1}-{2}-response-{3}-{4}.gif".format( fileNameTime, base36_plurk_id, str(thisPostMediaCount), str(response_count), owner_id )
					#imageNameWithoutPath = "{0}-plurk-{1}-response-{2}-{3}.jpg".format( fileNameTime, base36_plurk_id, str(response_count), owner_id )
					image_name = image_path + imageNameWithoutPath
					#image_name = fileNameTime + '-' + base36_plurk_id + '-' + str(
						#thisPostMediaCount) + '-' + "response" + '-' + str(
						#response_count) + '-' + owner_id + ".gif"
					#path = basePath + image_name
					if (os.path.isfile(image_name)):
						print( "[✗] {} was already downloaded.".format(imageNameWithoutPath))
						continue
					print('[✓] donwloading {}'.format(imageNameWithoutPath))
					with open(image_name, 'wb') as handler:
						handler.write(requests.get(str(responseLink)).content)

# https://stackoverflow.com/questions/3827065/can-i-use-a-multiprocessing-queue-in-a-function-called-by-pool-imap
def get_cursor(_plurk, _userName, _owner_id, _lowStandardFav):
	global plurk
	plurk = _plurk
	global userName
	userName = _userName
	global id
	id = _owner_id
	global lowStandardFav
	lowStandardFav = _lowStandardFav

	#parsePostsJob.q = _queue

if __name__ == "__main__":

	#old_stdout = sys.stdout
	#log_file = open("message.log","a")
	#sys.stdout = log_file
	
	t1 = time.time()

	plurk = plurkApiLogin()

	#userName = '' # User You Want To Crawl
	#inputUserName = mainUserName
	if( len(sys.argv) == 1 ):
		#print("Please enter at least one username OR several usernames with space separated:")
		userNamesList = input("Please enter at least one username OR several usernames with space separated:")
		userNamesList = userNamesList.split()
		#exit()
	else:
		userNamesList = sys.argv[1:]
	#for userName in sys.argv[1:]:
	for userName in userNamesList:
		userSearch = plurk.callAPI('/APP/UserSearch/search', {'query': userName})['users']

		if (len(userSearch) == 0):
			userPlurkUrl = 'https://www.plurk.com/' + userName
			userPlurkhtml = requests.get(userPlurkUrl, timeout=10)

			userExist = re.search(r"<title>.+</title>", userPlurkhtml.text)
			title = userExist.group()[7:]
			title = title[:-8]
			if (title != 'User Not Found! - Plurk'):
				# print("User Found!")
				settings = re.search(r"var\sSETTINGS\s=\s\{\S+user_id\":(\d+),\S+}", userPlurkhtml.text)
				id = int(settings.group(1))
				print("user id =", id)
			else:
				print("User Not Found!")
				exit()
		else:
			id = userSearch[0]['id']
			print(userSearch[0]['display_name'])
		
		print('userSearch\n',userSearch)
		
		path = './' + userName
		if not os.path.exists(path):
			os.mkdir(path);
		
		timeOffset = strftime("%Y-%m-%dT%H:%M:%S", gmtime())

		# q = mp.Queue()
		# q = mp.JoinableQueue()

		while (True):
			json = getPublicPlurks(plurk, id, timeOffset)
			if (len(json) == 0):
				break
			splitStr = json[-1]['posted'].split()
			abbr_to_num = {name: num for num, name in enumerate(calendar.month_abbr) if num}
			timeOffset = splitStr[3] + '-' + str(abbr_to_num[splitStr[2]]) + '-' + splitStr[1] + 'T' + \
						 splitStr[4]

			# print(timeOffset)
			"""
            old_stdout = sys.stdout
            log_file = open("timeOffset.log","a")
            sys.stdout = log_file
            print(timeOffset)
            sys.stdout = old_stdout
            log_file.close()
            """
			# Parse

			lowStandardFav = -1
			postCount = 0
			higherFavPostCount = 0
			downloadedMedia = 0
			response_media = 0

			pool = Pool(initializer=get_cursor, initargs=(plurk, userName, id, lowStandardFav))
			pool.map_async(parsePostsJob, json)

			pool.close()
		# pool.join()
		pool.join()

		# sys.stdout = old_stdout
		# log_file.close()

		"""
        reQ = q.task_done()
        print('state--->', reQ)
        print("&&&&&&&&&&&&&&&&&&&")
        while (not q.empty()):
            ppid = q.get()
            print(ppid)
            plurk_id_list.append( ppid )
            q.task_done()

        print("&&&&&&&&&&&&&&&&&&&")"""
		# print(plurk_id_list)

		# q.join()
		"""
        while (q.empty()):
            pool2 = Pool(initializer=get_cursor, initargs=(plurk, userName, id, lowStandardFav, q))
            p = pool2.map_async(getResponsesJob, plurk_id_list)  # map_async
            pool2.close()
            pool2.join()
            break
        """

		print("============================")
		# print(len(plurk_id_list))
		total_time = time.time() - t1
		print("Total time: {}\n".format(total_time) )
		# print("The average time crawling per post: ", total_time/len(plurk_id_list) if len(plurk_id_list) else 0)
