#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
The aim of the script is to train a Part of Speech (PoS) tagger.

* The train set for the PoS tagger
* For the purpose of the training an external maximun entropy model (megam)\
    is used.

After the PoS tagger has been created, it is pickled for subsequent use.
"""

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import logging
import pickle


# define logging configuration
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s')


def main():
    """ Main function. """
    # Regular expression used as a backoff tagger
    regex = nltk.RegexpTagger
    (
        [
            (r'^-?[0-9]+(.[0-9]+)?$', 'CD'),
            (
                r'('+'|'.join(stopwords.words('spanish')) + ')$', 'STOP'
            ),
            (
                r'(?:www\.|(?!www))[^\s\.]+\.[^\s]{2,}|www\.[^\s]+\.[^\s]{2,}',
                'URL'
            ),
            (r'[0-9]+/[0-9]+/[0-9]+', 'DATE'),
            (r'([^A-Za-z0-9])+', 'PUNCT'),
            (r'\xbf', 'Faa'),
            (r'\xa1', 'Fat'),
            (r'.*', 'N_N')  # weird tokens (default)
        ]
    )

    # Create training set from the Conll2002 Spanish corpus
    train_set = []
    for text in nltk.corpus.conll2002.tagged_sents('esp.train'):
        train_set.append([(word.lower(), tag) for word, tag in text])

    logging.info('Training Unigram Tagger...')
    unigram_tagger = nltk.UnigramTagger(train_set, backoff=regex)
    logging.info('Training Bigram Tagger...')
    tagger_da = nltk.BigramTagger(train_set, backoff=unigram_tagger)

    logging.info('Pickling Part of Speech Tagger...')
    pickle.dump(tagger_da, open("tmp/pos_tagger.p", "wb"))


def test_pos_tagger():
    """
        Test PoS tagger.
    """

    pos_tag = pickle.load(open("../tmp/POS_tagger.p", "rb"))
    string = "El presidente del congreso"
    tokens = [token.lower() for token in word_tokenize(string)]
    result = pos_tag.tag(tokens)

    assert result == [('el', 'DA'), ("presidente", 'NC'), ('del', 'SP'),
                      ('congreso', 'NC')]


if __name__ == '__main__':
    main()
