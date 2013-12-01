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
import datetime
from collections import defaultdict

def main():

	logging.info('Connecting to database ....')
	couch = couchdb.Server()
	database = couch['sentiments']
	logging.info('Established connection to db ...')

	valence = defaultdict(list)
	arousal = defaultdict(list)
	title = defaultdict(list)
	votes = defaultdict(list)

	for row in database.view('sentiments/sentiment'):
		date = datetime.date(row.key[0], row.key[1]+1, row.key[2])
		valence[date.isoformat()].append(row.value[2])
		arousal[date.isoformat()].append(row.value[1])
		title[date.isoformat()].append(row.value[3])
		votes[date.isoformat()].append(int(row.value[4]))
	
	average = []
	for date, valences in valence.iteritems():
		average.append({'date': date, 'valence': sum(valences)/len(valences), 
			'arousal': sum(arousal[date])/len(arousal[date]),
			'votes': sum(votes[date])/len(votes[date]),
			'title': '\n'.join(title[date])})

	f = open('sentiment_description.json', 'w')
	json.dump(average, f)
	f.close()


if __name__ == '__main__':
	logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)-8s %(message)s')
	main()