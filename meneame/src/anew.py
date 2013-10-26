# -*- coding: utf-8 -*-
"""
	@author: Albert

	Based on https://gist.github.com/fnielsen/4183541

"""

import csv
import re
import sys

# Spanish ANEW
csvfile = open('../data/ANEW.csv', 'r')
reader = csv.reader(csvfile, delimiter = ',')
reader.next() # skip headers

anew = dict([(row[2], float(row[3])) for row in reader])

# word splitter pattern
pattern_split = re.compile(r"\W+")

def sentiment(text):
	"""
		Returns a float for sentiment strength based on the input text.
	"""
	words = pattern_split.split(text.lower())
	sentiments = map(lambda word : anew.get(word, 0), words)
	print sentiments
	return 1

if __name__ == '__main__':
	text = 'Albert es un estúpido idiota'
	print text
	print '%.2f' % (sentiment(text))