#!/usr/bin/python
# -*- coding:utf-8 -*-

# ref: https://github.com/clsung/plurk-oauth 
# You can retrieve your app keys via the test tool at http://www.plurk.com/PlurkApp/
CONSUMER_KEY = ''
CONSUMER_SECRET = ''
ACCESS_TOKEN = ''
ACCESS_TOKEN_SECRET = ''

import multiprocessing as mp
from multiprocessing import Pool

import re
import json
import os
import urllib
from plurk_oauth import PlurkAPI
import requests
import calendar
import time
from time import gmtime, strftime
import itertools
from pprint import pprint
# https://stackoverflow.com/questions/1181919/python-base-36-encoding 
import base36

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

	#queue = args[1]
	print('id=',id)
	basePath = os.getcwd() + '\\'
	baseUrl = "https://www.plurk.com/p/"
	thisPostMediaCount = 0
	#multiInfoDict['postCount'] += 1
	#multiInfoDict['thisPostMediaCount'] = 0
	#print("!!!!!!!!!!!!!!!")
	#print(i)
	#print("!!!!!!!!!!!!!!!")
	if (i['owner_id'] != id):
		print("posted:", i['posted'])
		#print("@@@@@@@@@@replurk@@@@@@@@@@")
		return
	if (i['favorite_count'] > lowStandardFav):
		print("===================================================================================")
		#multiInfoDict['higherFavPostCount'] += 1
		owner_id_int = i['owner_id']
		owner_id = str(i['owner_id'])
		print("owner_id:", i['owner_id'])
		base36_plurk_id = str(base36.dumps(i['plurk_id']))
		print("postUrl:", baseUrl + base36_plurk_id)
		print("posted:", i['posted'])

		splitStr = i['posted'].split()
		abbr_to_num = {name: num for num, name in enumerate(calendar.month_abbr) if num}
		fileNameTime = splitStr[3] + '_' + str(abbr_to_num[splitStr[2]]) + '_' + splitStr[1]
		print("******************")
		print("porn:", i['porn'])
		print("favorite_count:", i['favorite_count'])
		print("response_count:", i['response_count'])
		pprint(i['content_raw'])  # type:str

		parsePostsJob.q.put(i['plurk_id'])

		_list = i['content'].split()
		for content in _list:
			if (content[0:4] == 'href'):
				content = content[:-1]
				if (content[-3:] == 'jpg'):
					if (re.match(url_validation_regex, str(content[6:])) is None):
						print("FALSE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
						continue
					if (urlExists(str(content[6:])) == False):
						print("FALSE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
						continue
					print(content[6:])
					#multiInfoDict['downloadedMedia'] += 1
					thisPostMediaCount += 1
					image_name = fileNameTime + '-' + base36_plurk_id + '-' + str(
						thisPostMediaCount) + '-' + owner_id + ".jpg"
					path = basePath + image_name
					if (os.path.isfile(path)):
						print(image_name, "was already downloaded.")
						#multiInfoDict['downloadedMedia'] -= 1
						continue
					with open(image_name, 'wb') as handler:
						handler.write(requests.get(str(content[6:])).content)
				elif (content[-3:] == 'png'):
					if (re.match(url_validation_regex, str(content[6:])) is None):
						print("FALSE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
						continue
					if (urlExists(str(content[6:])) == False):
						print("FALSE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
						continue
					print(content[6:])
					#multiInfoDict['downloadedMedia'] += 1
					thisPostMediaCount += 1
					image_name = fileNameTime + '-' + base36_plurk_id + '-' + str(
						thisPostMediaCount) + '-' + owner_id + ".png"
					path = basePath + image_name
					if (os.path.isfile(path)):
						print(image_name, "was already downloaded.")
						#multiInfoDict['downloadedMedia'] -= 1
						continue
					with open(image_name, 'wb') as handler:
						handler.write(requests.get(str(content[6:])).content)
				elif (content[-3:] == 'gif'):
					if (re.match(url_validation_regex, str(content[6:])) is None):
						print("FALSE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
						continue
					if (urlExists(str(content[6:])) == False):
						print("FALSE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
						continue
					print(content[6:])
					#multiInfoDict['downloadedMedia'] += 1
					thisPostMediaCount += 1
					image_name = fileNameTime + '-' + base36_plurk_id + '-' + str(
						thisPostMediaCount) + '-' + owner_id + ".gif"
					path = basePath + image_name
					if (os.path.isfile(path)):
						print(image_name, "was already downloaded.")
						#multiInfoDict['downloadedMedia'] -= 1
						continue
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
					#multiInfoDict['downloadedMedia'] += 1
					thisPostMediaCount += 1
					image_name = fileNameTime + '-' + base36_plurk_id + '-' + str(
						thisPostMediaCount) + '-' + owner_id + ".mp4"
					path = basePath + image_name
					if (os.path.isfile(path)):
						print(image_name, "was already downloaded.")
						#multiInfoDict['downloadedMedia'] -= 1
						continue
					#multiInfoDict['downloadedMedia'] += 1
					#multiInfoDict['thisPostMediaCount'] += 1
					with open(image_name, 'wb') as handler:
						handler.write(requests.get(str(content[6:])).content)
				else:
					print("others link:", content[6:])

		#getResponses(plurk, id, owner_id_int, owner_id, fileNameTime, base36_plurk_id, thisPostMediaCount)

		#parsePostsJob.q.put(i['plurk_id'])
		return i['plurk_id']



def getResponsesJob(pID):
	#userSearch = plurk.callAPI('/APP/UserSearch/search', {'query': userName})['users']
	#owner_id_int = userSearch[0]['id']

	print('pID=', pID)
	owner_id = str(id)

	res_raw_json = plurk.callAPI('/APP/Responses/get', {'plurk_id':pID} )
	basePath = os.getcwd() + '\\'
	base36_plurk_id = str(base36.dumps(pID))

	# for loop each responses
	response_count = 0
	response_media = 0
	thisPostMediaCount = 0
	for j in res_raw_json['responses']:

		if (j['user_id'] == id):
			splitStr = j['posted'].split()
			abbr_to_num = {name: num for num, name in enumerate(calendar.month_abbr) if num}
			fileNameTime = splitStr[3] + '_' + str(abbr_to_num[splitStr[2]]) + '_' + splitStr[1]

			#print("author content")
			res_content_raw = j['content_raw'].split()
			for responseLink in res_content_raw:
				if (responseLink[-4:] == '.jpg'):
					if (re.match(url_validation_regex, responseLink) is None):
						print("FALSE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
						continue
					if (urlExists(responseLink) == False):
						print("FALSE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
						continue
					response_media += 1
					response_count += 1
					#multiInfoDict['downloadedMedia'] += 1
					thisPostMediaCount += 1
					image_name = fileNameTime + '-' + base36_plurk_id + '-' + str(
						thisPostMediaCount) + '-' + "response" + '-' + str(
						response_count) + '-' + owner_id + ".jpg"
					path = basePath + image_name
					if (os.path.isfile(path)):
						#print(image_name, "was already downloaded.")
						#multiInfoDict['downloadedMedia'] -= 1
						continue
					with open(image_name, 'wb') as handler:
						handler.write(requests.get(str(responseLink)).content)
				elif (responseLink[-4:] == '.png'):
					if (re.match(url_validation_regex, responseLink) is None):
						print("FALSE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
						continue
					if (urlExists(responseLink) == False):
						print("FALSE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
						continue
					response_media += 1
					response_count += 1
					#multiInfoDict['downloadedMedia'] += 1
					thisPostMediaCount += 1
					image_name = fileNameTime + '-' + base36_plurk_id + '-' + str(
						thisPostMediaCount) + '-' + "response" + '-' + str(
						response_count) + '-' + owner_id + ".png"
					path = basePath + image_name
					if (os.path.isfile(path)):
						#print(image_name, "was already downloaded.")
						#multiInfoDict['downloadedMedia'] -= 1
						continue
					with open(image_name, 'wb') as handler:
						handler.write(requests.get(str(responseLink)).content)
				elif (responseLink[-4:] == '.gif'):
					if (re.match(url_validation_regex, responseLink) is None):
						print("FALSE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
						continue
					if (urlExists(responseLink) == False):
						print("FALSE!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
						continue
					response_media += 1
					response_count += 1
					#multiInfoDict['downloadedMedia'] += 1
					thisPostMediaCount += 1
					image_name = fileNameTime + '-' + base36_plurk_id + '-' + str(
						thisPostMediaCount) + '-' + "response" + '-' + str(
						response_count) + '-' + owner_id + ".gif"
					path = basePath + image_name
					if (os.path.isfile(path)):
						#print(image_name, "was already downloaded.")
						#multiInfoDict['downloadedMedia'] -= 1
						continue
					with open(image_name, 'wb') as handler:
						handler.write(requests.get(str(responseLink)).content)

# https://stackoverflow.com/questions/3827065/can-i-use-a-multiprocessing-queue-in-a-function-called-by-pool-imap
def get_cursor(_plurk, _userName, _owner_id, _lowStandardFav, _queue):
	global plurk
	plurk = _plurk
	global userName
	userName = _userName
	global id
	id = _owner_id
	global lowStandardFav
	lowStandardFav = _lowStandardFav

	parsePostsJob.q = _queue



if __name__ == "__main__":
	t1 = time.time()
	
	plurk = plurkApiLogin()	
	userName = ''  # USER YOU WANT TO CRAWL
	userSearch = plurk.callAPI('/APP/UserSearch/search', {'query': userName})['users']

	if (len(userSearch) == 0):
		userPlurkUrl = 'https://www.plurk.com/' + userName
		userPlurkhtml = requests.get(userPlurkUrl, timeout=10)
		id = 123
		print(userPlurkhtml)
		exit()
	# print(userName, " has block the search or you type a wrong userName.")
	else:
		id = userSearch[0]['id']
		print(userSearch[0]['display_name'])

	# pool = mp.Pool(8)
	timeOffset = strftime("%Y-%m-%dT%H:%M:%S", gmtime())

	plurk_id_list = []


	#q = mp.Queue()
	q = mp.JoinableQueue()
	
	pool = ""
	while (True):
		json = getPublicPlurks(plurk, id, timeOffset)
		if (len(json) == 0):
			break
		splitStr = json[-1]['posted'].split()
		abbr_to_num = {name: num for num, name in enumerate(calendar.month_abbr) if num}
		timeOffset = splitStr[3] + '-' + str(abbr_to_num[splitStr[2]]) + '-' + splitStr[1] + 'T' + \
					 splitStr[4]
		print(timeOffset)

		lowStandardFav = -1
		postCount = 0
		higherFavPostCount = 0
		downloadedMedia = 0
		response_media = 0
		# Parse
		pool = Pool(initializer=get_cursor, initargs=(plurk, userName, id, lowStandardFav,q))
		q.put( pool.map_async(parsePostsJob, json) ) #.map_async
	pool.close()
	pool.join()

	pool2 = Pool(initializer=get_cursor, initargs=(plurk, userName, id, lowStandardFav, q))
	p = pool2.map_async(getResponsesJob, plurk_id_list)  # map_async
	pool2.close()
	pool2.join()
	
	print("crawl", len(plurk_id_list), "plurk posts." )
	#print(plurk_id_list)
	print("Total time: ", time.time() - t1)
