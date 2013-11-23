#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Meneame scraper

Usage:
    meneame_scraper.py [options]

Options:
    -h, --help      show this screen.
    --version       show version.
    -o DIRECTORY    output directory [default: meneame].
    --start START   specify start page [default: 0].
    --timeout TIME  specify timeout after each request [default: 0].
    --range RANGE   specify the range. valid options\
 (24h | 48h | week | month | year | all) [default: 24h].

"""
import logging
import json
from menestats.scraper import scrap_page, scrap_comments
from docopt import docopt
from time import sleep
import os

def download_news(output, start=0, time_range=1, pause=1):
    """
        Download news
    """
    output_dir = os.path.join(output, 'raw')

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    current_page = start  # page counter
    more_news = True

    while more_news:
        stories = scrap_page(time_range, current_page)
        logging.info('Page %s: [%s]', current_page, ",".join([str(story.id) for story in stories]))
        for story in stories:
            filepath = os.path.join(output_dir, '%s.json' % story.id)
            if not os.path.exists(filepath):
                logging.debug('Downloading comments for %s', story.id)
                story.published, story.comments = scrap_comments(story.id)
                logging.debug('Writing %s ...', filepath)
                filename = open(filepath, 'w')
                json.dump(story.to_dict(), filename)
                filename.close()
                sleep(pause)
            else:
                logging.warning('File %s already exists...' % story.id)


        if not stories:
            more_news = False

        current_page += 1


if __name__ == '__main__':
    ARGS = docopt(__doc__, version='Meneame Scraper 1.0')

    # define logging configuration
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)-8s %(message)s')

    # transform the time range to index
    try:
        TIMERANGE = ['24h', '48h',
                            'week', 'month', 'year',
                            'all'].index(ARGS['--range'])
    except ValueError:
        logging.error('Error reading time range, not valid. Using default value [24h].')
        TIMERANGE = 0

    download_news(output=ARGS['-o'],
                  start=int(ARGS['--start']),
                  time_range=TIMERANGE,
                  pause=int(ARGS['--timeout']))
