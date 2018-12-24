#!/usr/bin/env python 

from getpass import getpass
from fbchat import log, Client
from fbchat.models import *
import yaml


def connection(config):
	client=Client(config['id'],config['psw'])
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

with open("config.yml", 'r') as ymlfile:
        config = yaml.load(ymlfile)
client=connection(config)
users = client.searchForUsers('Damien')
user = users[0]
print("User's ID: {}".format(user.uid))
print("User's name: {}".format(user.name))
print("User's profile picture url: {}".format(user.photo))
print("User's main url: {}".format(user.url))

message_id = client.send(Message(text='test'), thread_id=user.uid, thread_type=ThreadType.USER)

message_id = client.sendLocalImage('/home/tiictac/Images/Netflix/21891.png', message=Message(text='This is a local image'), thread_id=user.uid, thread_type=ThreadType.USER)

class EchoBot(Client):
    def onMessage(self, author_id, message_object, thread_id, thread_type, **kwargs):

        if message_object.text == 'like':
            log.info("{} from {} in {}".format(message_object, thread_id, thread_type.name))
            # If you're not the author, echo
            if author_id != self.uid:
                self.send(message_object, thread_id=thread_id, thread_type=thread_type)

client = EchoBot(config['id'],config['psw'])
client.listen()











#client=EchoBot(config['id'],config['psw'])
#client.listen()

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

