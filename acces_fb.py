#!/usr/bin/env python 

from getpass import getpass
from fbchat import log, Client
from fbchat.models import *
import yaml


def connection():
	with open("config.yml", 'r') as ymlfile:
	 	config = yaml.load(ymlfile)
	client=fbchat.Client(config['id'],config['psw'])
	return client

class EchoBot(Client):
    def onMessage(self, author_id, message, thread_id, thread_type, **kwargs):
        self.markAsDelivered(author_id, thread_id)
        self.markAsRead(author_id)

        log.info("Message from u {} in {} ({}): {}".format(author_id, thread_id, thread_type.name, message))
        self.sendMessage(message,thread_id=author_id,thread_type=ThreadType.USER)
        # If you're not the author, echo
        #if author_id != self.uid:
		#self.sendMessage(message, thread_id=thread_id, thread_type=thread_type)

#client=connection()
with open("config.yml", 'r') as ymlfile:
	 config = yaml.load(ymlfile)
client=EchoBot(config['id'],config['psw'])
client.listen()

# print("Hello")

# print(client.uid)
# client.
# test=client.searchForUsers("test")
# client.
# client.searchForUsers	
# # 
# client.sendMessage("Hello je te parle depuis mon script",thread_id=,thread_type=ThreadType.USER)

# no_of_friends = int(raw_input("Number of friends: "))
# for i in xrange(no_of_friends):
# 	name = str(raw_input("Name: "))
# 	friends = client.getUsers(name)  # return a list of names
# 	print(friends)

