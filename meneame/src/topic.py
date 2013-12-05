#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Meneame topic

Usage:
    topic.py [--window Number] [--topic Number] [--dbname DB]

Options:
    -h, --help      show this screen.
    --version       show version.
    --window Number     size of the time slice
    --topic Number      number of topics for the analysis
    --dbname DB   database where the text is stored [default: meneame].
"""

from topics.topic_analysis import get_topics
from topics.train_chunk_tagger import ConsecutiveNPChunker
from topics.train_chunk_tagger import ConsecutiveNPChunkTagger
import logging
import couchdb
from docopt import docopt
import pickle


# define logging configuration
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s')


def main(window, topics, dbname):
    """
        Main function.

          :param window: size of the time-slice
          :param topics: number of topics for the analysis
          :param dbname: the name of the database

    """

    couch = couchdb.Server()
    database = couch[dbname]
    logging.info('Established connection with the db %s', database)

    logging.info('Loading Part of Speech tagger')
    tagger = pickle.load(open("topics/tmp/pos_tagger.p", "rb")).tag

    logging.info('Loading Chunk tagger')
    chunker = pickle.load(open("topics/tmp/chunk_tagger.p", "rb")).parse

    get_topics(tagger, chunker, database, window, topics)

if __name__ == '__main__':
    ARGS = docopt(__doc__, version='Meneame Topics 1.0')
    main(ARGS['--window'], ARGS['--topic'], ARGS['--dbname'])
