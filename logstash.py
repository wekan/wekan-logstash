#!/usr/bin/env python
#
# logstash.py
#
# Simple tool that will print cards data for logstash (ELK Kibana)
#
# Author: Florent MONTHEL (fmonthel@flox-arts.net)
#
# {"storyPoint": 2.0, "nbComments": 1, "createdBy": "fmonthel", "labels": ["vert", "jaune"], "members": ["fmonthel", "test"], "id": "7WfoXMKnmbtaEwTnn", "createdAt": "2017-02-19T02:13:24.269Z", "lastModification": "2017-02-19T03:12:13.740Z", "list": "dsfds   refer", "dailyEvents": 5, "board": "Test", "isArchived": false}
# {"storyPoint": 2.0, "nbComments": 1, "createdBy": "fmonthel", "labels": ["vert", "jaune"], "members": ["fmonthel", "test"], "id": "7WfoXMKnmbtaEwTnn", "archivedAt": "2017-02-19T02:13:24.269Z", "createdAt": "2017-02-19T02:13:24.269Z", "lastModification": "2017-02-19T03:12:13.740Z", "list": "dsfds   refer", "dailyEvents": 5, "board": "Test", "isArchived": true}


#! /usr/bin/python

import os
import json
import datetime
from pymongo import MongoClient

# Parameters
mongo_user = 'admin'
mongo_password = 'admin123'
mongo_server = 'localhost'
mongo_port = '27017'
time_start = datetime.datetime.now()
date_start = datetime.datetime.today().date()

# Main function
def main() :
	
	cards = getCardsData()
	for id in cards :
		print json.dumps(cards[id])

# Get list of boards that will be in whitelist
def getWhiteListBoards() :
    
	lines = list()
	text_file = open(os.path.dirname(os.path.abspath(__file__)) + "/white-list-boards.txt", "r")
	lines = text_file.read().split('\n')
	text_file.close()
	return lines

# Function that will get in the title the first characters as storypoints
def getStoryPoint(title) :

	tmp = ""
	for l in title :
		if l in ['.', ',', ' ', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0']:
			tmp += l
		else:
			break
	try :
		return float(tmp)
	except ValueError :
		return 0

# Function that will populate dict for logstash
def getCardsData() :
	
	# BDD
	mongo = MongoClient('mongodb://' + mongo_user + ':' + mongo_password + '@' + mongo_server + ':' + mongo_port + '/')
	db = mongo['admin']
	users = db['users']
	boards = db['boards']
	lists = db['lists']
	cards = db['cards']
	card_comments = db['card_comments']
	activities = db['activities']
	
	# Get white list boards
	whitelistBoards = getWhiteListBoards()

	# Get cards data
	data = dict()
	for card in cards.find() :
	
		# Create index on id of the card
		data[ card["_id"] ] = dict()
		
		# Get id
		data[ card["_id"] ]['id'] = card["_id"]
		
		# Get archived data
		data[ card["_id"] ]['isArchived'] = card["archived"]
		if card["archived"] == True :
			# Get date of archive process
			if activities.find({"cardId": card["_id"], "activityType": "archivedCard"}).count() >= 1 :
				data[ card["_id"] ]["archivedAt"] = activities.find_one({"cardId": card["_id"], "activityType": "archivedCard"})["createdAt"]
				data[ card["_id"] ]["archivedAt"] = datetime.datetime.strftime(data[ card["_id"] ]["archivedAt"], "%Y-%m-%dT%H:%M:%S.000Z")
		
		# Get storypoint data
		data[ card["_id"] ]['storyPoint'] = getStoryPoint(card["title"])
		
		# Get created date data
		data[ card["_id"] ]['createdAt'] = datetime.datetime.strftime(card["createdAt"], "%Y-%m-%dT%H:%M:%S.000Z")
		
		# Get last activity date data (will be updated after)
		data[ card["_id"] ]['lastModification'] = card["dateLastActivity"]
		
		# Get number of comments data
		data[ card["_id"] ]['nbComments'] = card_comments.count({"cardId": card["_id"]})
		
		# Get creator name
		if users.find({"_id": card["userId"]}).count() == 1 :
			data[ card["_id"] ]['createdBy'] = users.find_one({"_id": card["userId"]})['username']
		else :
			data[ card["_id"] ]['createdBy'] = 'User not found'
		
		# Get list name
		if lists.find({"_id": card["listId"]}).count() == 1 :
			data[ card["_id"] ]['list'] = lists.find_one({"_id": card["listId"]})['title']
		else :
			data[ card["_id"] ]['list'] = 'List not found'
		
		# Get board data for board name and card title and label name
		if boards.find({"_id": card["boardId"]}).count() == 1 :
			# Get board data
			tmp_board = boards.find_one({"_id": card["boardId"]})
			data[ card["_id"] ]['board'] = tmp_board['title']
			# Public board or in whitelist => get title of cards ?
			if tmp_board["permission"] == 'public' or tmp_board["_id"] in whitelistBoards :
				# Get title data
				data[ card["_id"] ]['title'] = card["title"]
			else :
				# Get title data null
				data[ card["_id"] ]['title'] = ""
			# Get Labels name
			data[ card["_id"] ]["labels"] = list()
			if "labelIds" in card :
				for labelId in card["labelIds"] :
					# We will parse board label
					for label in tmp_board["labels"] :
						if labelId == label["_id"] :
							if "name" not in label or label["name"] == '' :
								data[ card["_id"] ]["labels"].append(label["color"])
							else :
								data[ card["_id"] ]["labels"].append(label["name"])
			if "labelIds" not in card or len(card["labelIds"]) == 0 :
				data[ card["_id"] ]['labels'].append('No label')
		else :
			data[ card["_id"] ]['board'] = 'Board not found'
			# Get title data null
			data[ card["_id"] ]['title'] = ""
		
		# Get members data
		data[ card["_id"] ]["members"] = list()
		if "members" in card :
			for member in card["members"] :
				if users.find({"_id": member}).count() == 1 :
					data[ card["_id"] ]['members'].append(users.find_one({"_id": member})['username'])
				else :
					data[ card["_id"] ]['members'].append('User not found')
		if "members" not in card or len(card["members"]) == 0 :
			data[ card["_id"] ]['members'].append('Unassigned')
		
		# Get daily events and update lastModification of card
		data[ card["_id"] ]["dailyEvents"] = 0
		for activity in activities.find({"cardId": card["_id"]}) :
			if activity["createdAt"].date() == date_start :
				data[ card["_id"] ]["dailyEvents"] += 1
			if activity["createdAt"] > data[ card["_id"] ]['lastModification'] :
				data[ card["_id"] ]['lastModification'] = activity["createdAt"]
		
		# Fornat the lastModification date now
		data[ card["_id"] ]['lastModification'] = datetime.datetime.strftime(data[ card["_id"] ]['lastModification'], "%Y-%m-%dT%H:%M:%S.000Z")
		
	# End, time to return dict :)
	return data

if __name__ == "__main__" :
	main()