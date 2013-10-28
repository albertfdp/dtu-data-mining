# -*- coding: utf-8 -*-
"""

"""

import nltk
from nltk.corpus import stopwords
from nltk.corpus import names as nltk_names
from jose_tokenizer import TreebankWordTokenizer

import logging

import pickle

def main():

    # Train POS tagger with Spanish corpus
    regexp_ES_tagger = nltk.RegexpTagger(
        [(r'^-?[0-9]+(.[0-9]+)?$', 'CD'),   # cardinal numbers
        (r'('+'|'.join(stopwords.words('spanish')) + ')$', 'STOP'), # StopWords    
        (r'[\]\\['+''.join([punct for punct in string.punctuation])+']$','PUNCT'),
        (r'(?:www\.|(?!www))[^\s\.]+\.[^\s]{2,}|www\.[^\s]+\.[^\s]{2,}','URL'),
        (r'[0-9]+/[0-9]+/[0-9]+','DATE'),
        (r'([^A-Za-z0-9])+','PUNCT'),
        (r'\xbf','Faa'),
        (r'\xa1','Fat'),
        (r'.*', 'N_N'),                      # weird nouns (default)
        ])
    
    train_set = []
    for text in nltk.corpus.conll2002.tagged_sents('esp.train'):
        train_set.append([(word.lower(),tag) for word,tag in text])
        
    logging.error('Training ES unigram')
    unigram_tagger = nltk.UnigramTagger(train_set, backoff=regexp_ES_tagger)
    logging.error('Training ES bigram')
    tagger_da = nltk.BigramTagger(train_set, backoff=unigram_tagger)
    logging.error('Saving Tagger')
    
    pickle.dump(tagger_da, open( "tmp/POS_tagger.p", "wb" ) )

if __name__ == '__main__':
	main()

