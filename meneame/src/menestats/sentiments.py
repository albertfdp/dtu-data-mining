# -*- coding: utf-8 -*-
"""
    Module that computes the sentiment for a given text and a given
    map with word => (valence, arousal)
"""
from nltk.tokenize import PunktWordTokenizer
from nltk.stem import SnowballStemmer

STEMMER = SnowballStemmer('spanish')


def get_sentiment(sentiment_db, txt):
    """
        Returns a tuple with the valence and arousal strength
        based on the input text. Returns null in case it cannot
        be computed.
    """
    words = PunktWordTokenizer().tokenize(txt)
    try:
        sentiments = map(lambda word: sentiment_db.get(
            stemmer.stem(word), None), words)
        sentiments = filter(None, sentiments)
    except IndexError:
        sentiments = None
    if sentiments:
        valences = [s['valence'] for s in sentiments if s is not None]
        arousals = [s['arousal'] for s in sentiments if s is not None]
        valence = float(sum(valences))/len(valences)
        arousal = float(sum(arousals))/len(arousals)
        return valence, arousal
    else:
        return None


def test_get_sentiments():
    """
        Test get_sentiment function.
    """

    import os
    import csv

    csvfile = open(os.path.join(os.path.dirname(__file__),
                   'test_anew.csv'), 'r')

    reader = csv.reader(csvfile, delimiter=',')
    reader.next()  # skip headers
    anew = dict([(STEMMER.stem(unicode(row[2], 'utf-8')),
                  {'valence': float(row[3]),
                   'arousal': float(row[5])}) for row in reader])

    text = """En realidad los filósofos griegos importantes \
odiaban la democracia (ENG)"""

    valence, arousal = get_sentiment(anew, text.decode('utf-8'))
    assert valence == 1.74
    assert arousal == 7.01
