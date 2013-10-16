# -*- coding: utf-8 -*-
"""
Created on Mon Oct  7 16:52:55 2013

@author: ferdinando
"""

import couchdb
#import json
import logging
#from pprint import pprint
#import hashlib
import sys
from bs4 import BeautifulSoup

def stripHtmlTags(html):
       return ''.join( BeautifulSoup(html).findAll(text=True)) 


logging.basicConfig(filename='cleaner.log',level=logging.DEBUG, filemode='w')
logging.basicConfig(format='%(asctime)s %(message)s')


#Connection with the databases
try:
    couch = couchdb.Server()
    news_db = couch['meneame']
    sha_db = couch['sha']
except Exception, err:
    logging.exception("Problem with retrieving the databases \n")
    logging.exception(err)    
    sys.exit(1)
    
logging.info('Connection to the databases estabilished')

#TODO: add try excepts?
for el in news_db:    
    
    logging.info('Considering news ' + el)
    news = dict(news_db.get(el))

    comments = news['comments']    
    commenters = dict()
        
    for comment in comments:
        user = comment['user']        
        #Adding to the commenters list
        commenters.setdefault(user,0)
        commenters[user] = commenters[user] + 1
            
        #Adding the cleaned version of the summary
        cleaned_comment = stripHtmlTags(comment['summary'])
        comment['cleaned_summary'] = cleaned_comment
        

    news['commenters']=commenters
    news_db.save(news)
