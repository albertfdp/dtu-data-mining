#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
The aim of the script is to query the news data base in order to merge the\
news with each of the topics assigned to them

* The following dataset are unpickled:
    * topics_dist : Dictionary of topic ids and words

The final dataset containing everything is saved in a JSON file.
"""


import couchdb
from couchdb.design import ViewDefinition

try:
    import jsonlib2 as json
except ImportError:
    import json

from collections import defaultdict
import logging
import pprint

import pickle


def main():
    """Main function"""

    couch = couchdb.Server()
    topics_db = couch['meneame_topic_test_slices_2']
    news_db = couch['meneame']
    topic_dist = pickle.load(open("tmp/topic_SLICES_dist_aux.p", "rb"))

    news = {}
    for post in news_db:
        new_aux = dict(news_db.get(post))
        new = {}
        new['description'] = new_aux['description']
        new['title'] = new_aux['title']
        
        news['_id'] = new

    for topic in topics_db:
        aux = dict(topics_db.get(topic))
        data = news[aux['article_id']]

        data['topic_id'] =  aux['topic_id']    
        data'slice_id'] =  aux['slice_id'] 
        data['slice_date'] =  aux['slice_date']

        news[aux['article_id']] = data    

if __name__ == '__main__':
    main()
