#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
The aim of the script is to query the news data base in order to extract the\
description of each new, group them in an 10-day time slice window and infer\
the latent topics.

* The PoS tagger and the Chunk tagger are unpickled for later use.\
* The scripts pickles:\
     - The Topic Distribution (topic_dist): Topic_id + words per topics\
     - The Topic Slices (topic_slice): Slice_Date + array of topic_ids\

"""

import sys
import time
from dateutil import parser
import couchdb
import networkx as nx
from collections import defaultdict
import nltk
from nltk.corpus import stopwords
from gensim import corpora, models
from topics.meneame_tokenizer import TreebankWordTokenizer
import logging
import numpy as np
from topics.train_chunk_tagger import ConsecutiveNPChunker
from topics.train_chunk_tagger import ConsecutiveNPChunkTagger


# define logging configuration
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)-8s %(message)s')


def tokenize_text(time_slice, sent_tokenizer):
    """
    Tokenize all the text included in time_slice and returns\
    arrays of tokens

    :param time_slice: Array of texts and texts ids

    """

    texts = []
    # Get topics for the previous timeslice
    objects_ids = []
    for text, text_id in time_slice:
        words = []
        for sentence in sent_tokenizer.tokenize(text):
            tokens = [
                token.lower()
                for token in TreebankWordTokenizer().tokenize(sentence)
            ]
            words.extend(tokens)
        objects_ids.append(text_id)
        texts.append(words)

    return texts


def test_tokenize_text():
    """
    Test the tokenize_text function

    """

    sent_es_token = nltk.data.load('tokenizers/punkt/spanish.pickle')
    result = tokenize_text([["Example to tokenize", 1]], sent_es_token)
    assert result == [["example", "to", "tokenize"]]


def extract_entities(texts, pos_tagger, chunk_tagger):
    """
    Extract entities (named entities, like persons and organizations,\
    and nouns) from arrays of tokens

    :param texts: Array of tokens
    :param pos_tagger: Part of Speech tagger
    :param chunk_tagger: Chunk tagger

    """

    nouns = ['NC', 'N_N', 'NP']
    entities = []
    stop_w = stopwords.words('spanish')

    for tokens in texts:
        words = []
        pos_tokens = pos_tagger(tokens)
        named_tokens = chunk_tagger(pos_tokens)
        for token in named_tokens:
            if type(token) == nltk.tree.Tree:
                words.append(
                    ' '.join(
                        [
                            i[0] for i in token.leaves()
                            if len(i[0]) > 2 and len(i[0]) < 20
                        ]
                    )
                )
            else:
                if len(token[0]) <= 2 or len(token[0]) >= 20:
                    continue
                if token[1] not in nouns:
                    continue
                if token[0].lower().strip('.').encode('utf-8') in stop_w:
                    continue

                words.append(token[0])

        entities.append(words)

    return entities


def hellinger_distance(prob_a, prob_b):
    """
    Calculates the Hellinger distance between p and q.

    :param p: Probability distribution over a vocabulary
    :param q: Probability distribution over a vocabulary


    """
    i = [t[0] for t in sorted(prob_a, key=lambda word: word[1])]
    j = [t[0] for t in sorted(prob_b, key=lambda word: word[1])]

    return 1 - np.sqrt(np.sum((np.sqrt(i) - np.sqrt(j)) ** 2)) / np.sqrt(2)


def test_hellinger_distance():
    """
    Test the hellinger_distance function

    """
    prob_a = [(0.25, 'A'), (0.25, 'B'), (0.25, 'C'), (0.25, 'D')]
    prob_b = [(0.25, 'A'), (0.25, 'B'), (0.25, 'C'), (0.25, 'D')]
    result = hellinger_distance(prob_a, prob_b)
    assert result == 1.0

    prob_a = [(0.25, 'A'), (0.25, 'B'), (0.25, 'C'), (0.20, 'D'), (0.05, 'E')]
    prob_b = [(0.2, 'A'), (0.2, 'B'), (0.2, 'C'), (0.2, 'D'), (0.2, 'E')]
    result = hellinger_distance(prob_a, prob_b)
    assert result == 0.82917960675006308


def merging_topics(topic_dist, topic_list, threshold, sim_metric):
    """
    Calculates similarities between a list of topics and merge them if their\
    similarity is greater than a threshold

    :param topic_dist: Dictionary of topic ids and associated words
    :param topic_list: Array of topics as probability distributions
    :param threshold: Value to check if two topics are similar
    :param sim_metric: Function to compare topics

    """

    # Get similarties between topics
    topics_score = defaultdict(list)
    index_a = 0
    for topic_a in topic_list:
        index_b = 0
        for topic_b in topic_list:
            if index_a != index_b:
                score = sim_metric(topic_a, topic_b)
                topics_score[index_a].append({index_b: score})
            index_b += 1
        index_a += 1

    # Check similarity between topics grouping similar topics (score > 0.7)
    # making edges between them in a network
    graph = nx.Graph()
    for topic_key in topics_score:
        # Order according to max similarity
        score_list = sorted(
            topics_score[topic_key],
            key=lambda x: x.items()[0][1],
            reverse=True
        )
        for topic_value in score_list:
            if topic_value.values()[0] > threshold:
                graph.add_edge(topic_value.keys()[0], topic_key)
            else:
                graph.add_edge(topic_key, topic_key)

    components = nx.connected_components(graph)

    topic_dict = {}
    topic_ids_in_slice = []

    # All the topics in a component represent the same topic
    for i in components:
        # All the topics in the component have the same id
        # id = len(topic_dist)
        for topic_id in i:
            topic_dict[topic_id] = len(topic_dist)

        # We always choose the first topic of the component
        # as representative of all the topics in the component
        topic_dist[len(topic_dist)] = topic_list[i[0]]
        topic_ids_in_slice.append(len(topic_dist))

    return (topic_dict, topic_ids_in_slice)


def get_topics(tagger_es, chunker_es, news_db, window_size=10, num_topics=35):
    """Main function"""

    ini = time.time()
    couch = couchdb.Server()
    try:
        topic_db = couch.create('meneame_topic_db')
    except Exception:
        topic_db = couch['meneame_topic_db']

    logging.info('Loading Spanish Sent Tokenizer')
    sent_es_token = nltk.data.load('tokenizers/punkt/spanish.pickle')

    logging.info('Creating news corpus...')
    news = []
    for post in news_db:
        new = dict(news_db.get(post))
        news.append(
            {
                'published': parser.parse(new['published']),
                'description': new['description'],
                '_id': new['_id']
            }
        )

    # Order news by date
    ordered_news = sorted(news, key=lambda element: element['published'])
    last_date = ''
    index = 0
    mssg_id = 0
    len_query = len(ordered_news)
    topic_dist = dict()
    time_slices = defaultdict(list)
    topic_slices = {}

    logging.info('Creating time slices...')
    for post in ordered_news:
        # Group articles in a "window_size"-day window
        if index == 0:  # first time
            last_date = post['published']
            index += 1

        if (post['published'] - last_date).days < window_size:
            if post['description'] is not None:
                time_slices[last_date].append(
                    [post['description'], post['_id']]
                )
                sys.stderr.write(
                    'ids:%d [%f]\r' %
                    (mssg_id, float(mssg_id*100)/float(len_query))
                )
                mssg_id += 1
        else:
        # New 10-day timeslice
            # Creating tokens
            texts = tokenize_text(time_slices[last_date], sent_es_token)

            # Extract entities
            entities = extract_entities(texts, tagger_es, chunker_es)

            # Discard tokens that appear once
            tokens = sum(entities, [])
            lonely_tokens = set(
                word for word in set(tokens) if tokens.count(word) == 1
            )
            texts = [
                [word for word in entity if word not in lonely_tokens]
                for entity in entities
            ]

            dictionary = corpora.Dictionary(texts)
            corpus = [dictionary.doc2bow(text) for text in texts]

            # Creating TF-IDF corpus
            tfidf = models.TfidfModel(corpus)
            corpus_tfidf = tfidf[corpus]

            # Create LDA model
            model = models.ldamodel.LdaModel(
                corpus_tfidf,
                id2word=dictionary,
                num_topics=num_topics,
                update_every=1,
                chunksize=20,
                passes=1
            )

            topic_list = []
            # Extract Topics from model
            for i in range(num_topics):
                # Get all the words of the probability distribution
                topic = model.show_topic(i, len(dictionary))
                topic_list.append(topic)

            # Merge topics if their similarity score is greater than 0.7
            topic_dict, topic_ids_in_slice = merging_topics(
                topic_dist,
                topic_list,
                0.7,
                hellinger_distance
            )

            topic_dist_per_slice = [new for new in model[corpus_tfidf]]
            #Once we have the topics, assign them to the news in the DB
            for text, id_new in time_slices[last_date]:
                # Order topics for each new according to the most
                # representative, and select it
                best_topic = sorted(
                    topic_dist_per_slice[index],
                    key=lambda t: t[1],
                    reverse=True
                )[0]
                topic_db.save(
                    {
                        "article_id": id_new,
                        "topic_id": topic_dict[best_topic[0]],
                        "slice_id": len(topic_slices),
                        "slice_date": last_date.strftime('%d/%m/%Y')
                    }
                )

            topic_slices[last_date] = topic_ids_in_slice

            # Update new time_lice date
            last_date = post['published']
            if post['description'] is not None:
                time_slices[last_date].append(
                    [post['description'], post['_id']]
                )
            sys.stderr.write(
                'ids:%d [%f]\r' %
                (mssg_id, float(mssg_id*100)/float(len_query))
            )
            mssg_id += 1

    fin = time.time()
    logging.info('Time consumed: %f' % ((float(fin)-float(ini))/60/60))
