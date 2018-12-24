#!/usr/bin/env python


import urllib, json
import sqlite3
import requests
import re
from getpass import getpass
from fbchat import log, Client
from fbchat.models import *
import yaml
import os.path
import argparse


taille_page=50

###### Menu 
parser = argparse.ArgumentParser()
parser.add_argument("-f", "--file", help="yaml file",required="TRUE")
args = parser.parse_args()
### Load Config file
yaml_file=args.file



####Fb function pour afficher si le message est "like"
class EchoBot(Client):
	    def onMessage(self, author_id, message_object, thread_id, thread_type, **kwargs):
	    	log.info("{} from {} in {}".format(message_object.text, thread_id, thread_type.name))
	        if message_object.text == 'like':
	            print(log.info("{} from {} in {}".format(message_object, thread_id, thread_type.name)))
	    #def search(query, fetch_messages=False, thread_limit=5, message_limit=5):


##### Fonction pour se connecter a fb
def connection(config):
	client=EchoBot(config['id'],config['psw'])
	return client

### Open Yaml file
with open(yaml_file, 'r') as ymlfile:
        config = yaml.load(ymlfile)

client=EchoBot(config['id'],config['psw'])
### Load parameters
folder_images=config['folder_to_save_images']
path_db=config['path_to_data_base']
languages=config['languages']
###Connect to db
conn = sqlite3.connect(path_db)
cursor = conn.cursor()




######## Creation des table
print("Create or Load database ... ")
try:
	cursor.execute("""
		CREATE TABLE IF NOT EXISTS film(
	     id_film TEXT PRIMARY KEY  UNIQUE,
	     title TEXT,
	     title_fr TEXT,
	     path_ima TEXT,
	     send  TEXT DEFAULT 'no',
	     chaine TEXT,
	     date_sortie TEXT
	)
	""")
	conn.commit()
	cursor.execute("""
		CREATE TABLE IF NOT EXISTS t_langue(
	     langue TEXT PRIMARY KEY  UNIQUE
	)
	""")
	conn.commit()
	cursor.execute("""
		CREATE TABLE IF NOT EXISTS link(
		 id_film TEXT,
		 langue TEXT,
		 PRIMARY KEY(`id_film`,`langue`),
	     FOREIGN KEY(id_film) REFERENCES film(id_film),
	     FOREIGN KEY(langue) REFERENCES t_langue(langue)
	)
	""")
	conn.commit()
except sqlite3.OperationalError:
	print('Erreur la table existe deja')


###### Ajout des langue a la base de donnee
langue_already_record=[]
cursor.execute("""SELECT langue FROM t_langue""")
for i in cursor:
	langue_already_record.append(i[0])

for item in languages:
	if item not in langue_already_record:
		cursor.execute("""
	 	 INSERT INTO t_langue(langue) 	VALUES(?)""", (item,))
		conn.commit()





#### Recupere les nouveaux films de toutes les langues
#### et les met dans un dictionnaire
#### Si le film a deja une image l'ecrase pour l'affiche du film en Fr sinon ne l'ecrase pas
#### Si la langue est FR recupere aussi les info de amazon prime
tot_dic={}

for l in languages:
	print "Loading movies in "+l+" ... "
	
	if l == "fr_FR":
		provider="nfx\",\"prv"
	else:
		provider="nfx"
	url = 'https://apis.justwatch.com/content/titles/'+l+'/new?body={"age_certifications":null,"content_types":["movie"],"genres":null,"languages":null,"max_price":null,"min_price":null,"monetization_types":["flatrate","ads","rent","buy","free"],"page":1,"page_size":'+str(taille_page)+',"presentation_types":null,"providers":["'+provider+'"],"release_year_from":null,"release_year_until":null,"scoring_filter_types":null,"timeline_type":null,"titles_per_provider":100}'
	print(url)
	response = urllib.urlopen(url)
	data = json.loads(response.read())
	for i in range(len(data['days'])):
		if data['days'][i]['providers'][0]['provider_id'] == 8:
			chaine="Netflix"
		else:
			if data['days'][i]['providers'][0]['provider_id'] == 119:
				chaine="Amazon"
			else:
				chaine = "Inconnue"
		for m in range(len(data['days'][i]['providers'][0]['items'])):
			ID_film=data['days'][i]['providers'][0]['items'][m]['id']
			title_original=data['days'][i]['providers'][0]['items'][m]['original_title']
			try:
				mynewstring = title_original.encode('ascii')
			except UnicodeEncodeError:
				title_original=data['days'][i]['providers'][0]['items'][m]['title']
			title_original=title_original.replace(" ","_")
			if l == "fr_FR":
				titre_fr=data['days'][i]['providers'][0]['items'][m]['title']
				titre_fr=titre_fr.replace(" ","_")
			else:
				titre_fr=""
			annee_de_sortie=data['days'][i]['providers'][0]['items'][m]['original_release_year']
			if "poster" in data['days'][i]['providers'][0]['items'][m]:
				name_film=data['days'][i]['providers'][0]['items'][m]['full_path']
				name_film=name_film.rsplit('/', 1)[1]
				poster=data['days'][i]['providers'][0]['items'][m]['poster']
				poster=poster.rsplit('/', 1)[0]
				path_image="https://images.justwatch.com"+poster+"/s166/"+name_film
				image=folder_images+str(ID_film)+".png"
				if os.path.exists(image):
					if l == "fr_FR":
						r = requests.get(path_image, allow_redirects=True)
						open(image, 'wb').write(r.content)
				else:
					r = requests.get(path_image, allow_redirects=True)
					open(image, 'wb').write(r.content)
			else:
				image=""
			tot_dic[ID_film]={'chaine':chaine,'original_title':title_original,'titre_fr':titre_fr,'date_sortie':annee_de_sortie,'path_image':image,'pays':l}


				
#### Compare les film deja existant dans la base de donnees
#### pour les films non present :
####  --> Rajoute dans la base
#### pour les films present :
####  --> Rajoute nom fr 

id_in_db=[]
cursor.execute("""SELECT id_film FROM film""")
for i in cursor:
	id_in_db.append(i[0])


for key, value in tot_dic.iteritems():
	value['ID_film']=key
	if str(key) in str(id_in_db):
		if value['pays'] == "fr_FR":
			if value['path_image'] != "":
				cursor.execute("""UPDATE film SET title_fr = :titre_fr WHERE id_film = :ID_film""",value)
				conn.commit()
		try:
			cursor.execute("""
			INSERT INTO link(id_film, langue) 
			VALUES(:ID_film, :pays)""", value)
			conn.commit()
		except sqlite3.IntegrityError:
			pass
	else:
		cursor.execute("""
		INSERT INTO film(id_film, title,title_fr,path_ima,chaine,date_sortie) 
		VALUES(:ID_film, :original_title, :titre_fr, :path_image, :chaine, :date_sortie)""", value)
		conn.commit()
		cursor.execute("""
		INSERT INTO link(id_film, langue) 
		VALUES(:ID_film, :pays)""", value)
		conn.commit()


#### Envoie des nouveaux films dans la base sur fb
print("Send new movies to fb ")
users = client.searchForUsers('Damien')
user = users[0]
cursor.execute("""SELECT title, title_fr, path_ima,id_film FROM film  WHERE send = ? """,("no",))
rows = cursor.fetchall()
for row in rows:
	titre_original=row[0].replace("_"," ")
	titre_fr=row[1].replace("_"," ")
	id_film=row[3]
	if titre_fr == "":
		titre=titre_original
	else:
		titre=titre_fr+" ("+titre_original+")"
	if(row[2] == ""):
		message_id = client.send(Message(text=titre), thread_id=user.uid, thread_type=ThreadType.USER)
	else:
		message_id = client.sendLocalImage(row[2], message=Message(text=titre), thread_id=user.uid, thread_type=ThreadType.USER)
	cursor.execute("""UPDATE film SET send = ? WHERE id_film = ?""",("yes",id_film))
	conn.commit()

conn.close()
# client.listen()
# client.doOneListen()
#conn.close()

