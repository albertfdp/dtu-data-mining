#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
The aim of this script is to load the articles json files to the couchdb\
database. The id in the db is set to be the same as the identifier of the\
article on the meneame webiste.

Usage:
    to_database.py [--input MENEAME] [--db DATABASE]

Options:
    -h, --help      show this screen.
    --version       show version.
    --input INPUT   input folder.
    --db DATABASE    output database [default: meneame].

"""
from docopt import docopt
import os
import couchdb
import json
import logging
import sys


def main(path, dbname):
    """ Main function. """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)-8s %(message)s')

    #Connection with the database
    try:
        couch = couchdb.Server()
        database = couch[dbname]
    except couchdb.ResourceNotFound, err:
        logging.exception("Connection error with the database! \n")
        logging.exception(err)
        sys.exit(1)

    logging.info('Connection to the server estabilished')

    if not os.path.exists(path):
        logging.error('Input folder %s does not exists', path)
        sys.exit(1)

    json_news = [doc for doc in os.listdir(path) if doc.endswith(".json")]

    for news in json_news:
        news_document = json.load(open(os.path.join(path, news)))
        doc_id = str(news_document['_id'])
        news_document['_id'] = doc_id
        if database.get(doc_id) is None:
            database.save(news_document)
            logging.info('Document {0} saved'.format(doc_id))
        else:
            logging.info('Document {0} was already saved'.format(doc_id))


if __name__ == '__main__':
    ARGS = docopt(__doc__, version='Meneame Scraper 1.0')
    main(ARGS['--input'], ARGS['--db'])
