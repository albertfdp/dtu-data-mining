# -*- coding: utf-8 -*-
"""
@author: ferdinando
"""

import os
import couchdb
import json
import logging

#from pprint import pprint
logging.basicConfig(filename='to_couchdb.log',level=logging.DEBUG)
logging.basicConfig(format='%(asctime)s %(message)s')


#Connection with the database
couch = couchdb.Server()

db = couch['meneame']
logging.info('Connection to the server estabilished')



#Find files
path = "./json_news/"
json_news = [doc for doc in os.listdir(path) if doc.endswith(".json")]

for news in json_news:
    news_document = json.load(open(path+doc))
    doc_id = str(news_document['id'])
    news_document['_id'] = doc_id
    if db.get(doc_id)==None:
        db.save(news_document)
        logging.debug('Document {0} saved'.format(doc_id))
    else:
        logging.debug('Document {0} was already saved'.format(doc_id))

        
        



