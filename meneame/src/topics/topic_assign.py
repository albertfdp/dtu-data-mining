#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
The aim of the script is to query the news data base in order to merge the\
news with each of the topics assigned to them.

The final dataset containing all the information is saved in a JSON file.
"""


import couchdb
try:
    import jsonlib2 as json
except ImportError:
    import json
import logging

# define logging configuration
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s')


def main():
    """Main function"""

    couch = couchdb.Server()
    topics_db = couch['meneame_topic_db']
    news_db = couch['meneame']
    logging.info('Loading topic distribution...')

    logging.info('Retrieving news from DB...')
    news = {}
    for post in news_db:
        new = dict(news_db.get(post))
        news[new['_id']] = {
            'description': new['description'],
            'title': new['title'],
            'votes': new['votes']
        }

    logging.info('Merging news and topics...')
    for topic in topics_db:
        aux = dict(topics_db.get(topic))
        data = news[aux['article_id']]

        data['topic_id'] = aux['topic_id']
        data['slice_id'] = aux['slice_id']
        data['slice_date'] = aux['slice_date']

        news[aux['article_id']] = data

    logging.info('Generating JSON files...')
    json.dump(news, open('../web/meneapp/assets/data/topic_news.json', 'w'))


if __name__ == '__main__':
    main()
