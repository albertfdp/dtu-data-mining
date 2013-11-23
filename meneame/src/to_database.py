#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
The aim of this script is to load the articles json files to the couchdb\
database. The id in the db is set to be the same as the identifier of the\
article on the meneame webiste.
"""

import os
import couchdb
import json
import logging
import sys


def main():
    """ Main function. """
    logging.basicConfig(filename='to_couchdb.log',
                        level=logging.DEBUG, filemode='w')
    logging.basicConfig(format='%(asctime)s %(message)s')

    #Connection with the database
    try:
        couch = couchdb.Server()
        db = couch['meneame']
    except couchdb.ResourceNotFound, err:
        logging.exception("Connection error with the database! \n")
        logging.exception(err)
        sys.exit(1)

    logging.info('Connection to the server estabilished')

    path = "../data/news/"
    json_news = [doc for doc in os.listdir(path) if doc.endswith(".json")]

    for news in json_news:
        news_document = json.load(open(path + news))
        doc_id = str(news_document['id'])
        news_document['_id'] = doc_id
        if db.get(doc_id) is None:
            db.save(news_document)
            logging.debug('Document {0} saved'.format(doc_id))
        else:
            logging.debug('Document {0} was already saved'.format(doc_id))


if __name__ == '__main__':
    main()
