#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Meneame scraper

Usage:
    meneame_scraper.py [options]

Options:
    -h, --help      show this screen.
    --version       show version.
    -o DIRECTORY    output directory [default: mename].
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
        for story in stories:
            filepath = os.path.join(output_dir, '%s.json' % story.id)

            if not os.path.exists(filepath):
                logging.debug('Downloading comments for %s', story.id)
                story.published, story.comments = scrap_comments(story.id)
                logging.info('Writing %s ...', filepath)
                filename = open(filepath, 'w')
                json.dump(story.to_dict(), filename)
                filename.close()

        if not stories:
            more_news = False

        current_page += 1
        sleep(pause)


if __name__ == '__main__':
    ARGS = docopt(__doc__, version='Meneame Scraper 1.0')

    # define logging configuration
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s %(levelname)-8s %(message)s')

    # transform the time range to index
    TIMERANGE = ['24h', '48h',
                         'week', 'month', 'year',
                         'all'].index(ARGS['--range'])

    download_news(ARGS['-o'],
                  int(ARGS['--start']),
                  TIMERANGE,
                  int(ARGS['--timeout']))
