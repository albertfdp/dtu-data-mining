#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Meneame sentiments

Usage:
    meneame_sentiment.py [--input FILE] [--database DB] [--output FILE]

Options:
    -h, --help      show this screen.
    --version       show version.
    --database DB   database where the text is stored [default: meneame].
    --input ANEW    input ANEW file
    --output FILE   output file where to save the\
 results [default: sentiments.json]

"""
import csv
import logging
import json
import couchdb
from nltk.stem import SnowballStemmer
from menestats.sentiments import get_sentiment
from docopt import docopt
import os
import sys


def main(input_file, dbname, output):
    """
        Main function
    """

    # read ANEW file
    if not os.path.exists(input_file):
        logging.error('File %s does not exist', input_file)
        sys.exit(1)
    else:
        csvfile = open(input_file, 'r')
        reader = csv.reader(csvfile, delimiter=',')
        reader.next()  # skip headers
        stemmer = SnowballStemmer('spanish')
        anew = dict([(stemmer.stem(unicode(row[2], 'utf-8')),
                      {'valence': float(row[3]),
                       'arousal': float(row[5])}) for row in reader])

    couch = couchdb.Server()
    database = couch[dbname]
    logging.info('Established connection with the db %s', dbname)

    for element in database:
        doc = database.get(element)

        comments = " ".join([comment['cleaned_summary']
                            for comment in doc['comments']])
        description = " ".join([database.get(element)['title'],
            doc['description']])

        sentiment_comments = get_sentiment(anew, comments)
        sentiment_description = get_sentiment(anew, description)

        if sentiment_comments is not None and sentiment_description is not None:
            logging.info('%s val: %.2f - %.2f aro: %.2f - %.2f : %s',
                doc.id, sentiment_comments[0], sentiment_description[0],
                sentiment_comments[1], sentiment_description[1], doc['title'])
            doc['sentiments'] = {'comments':
                                {'valence': sentiment_comments[0],
                                 'arousal': sentiment_comments[1]},
                                 'description':
                                {'valence': sentiment_description[0],
                                'arousal': sentiment_description[1]}}
            database.save(doc)

        else:
            logging.warn('%s could not be analyzed. skiping ...',
                         database.get(element)['title'])

if __name__ == '__main__':
    ARGS = docopt(__doc__, version='Meneame Scraper 1.0')
    main(ARGS['--input'], ARGS['--database'], ARGS['--output'])

    # define logging configuration
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(levelname)-8s %(message)s')
