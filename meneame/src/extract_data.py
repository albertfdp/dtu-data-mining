#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
The aim of this script is to generate a JSON file to feed the\
visualizations of the website.

"""
import couchdb
import json
import logging
import datetime
from collections import defaultdict

def main():
    """
        Main function. Connects to the database and generates\
        a JSON file with the average sentiment per day.
    """
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

    filename = open('sentiment_description.json', 'w')
    json.dump(average, filename)
    filename.close()


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)-8s %(message)s')
    main()
