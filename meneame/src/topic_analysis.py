# -*- coding: utf-8 -*-
"""

"""

import sys
from datetime import date, datetime

import couchdb

try:
    import jsonlib2 as json
except ImportError:
    import json

from collections import defaultdict
import Levenshtein


import nltk
import string
from nltk.corpus import stopwords
from nltk.stem import SnowballStemmer
from gensim import corpora, models
import langid
from nltk.corpus import names as nltk_names
from jose_tokenizer import TreebankWordTokenizer

import logging

from numpy import zeros, array
from math import sqrt, log


def main():

    couch = couchdb.Server()
    news_db = couch['meneame']
    
    languages = ['es','en','dk']
    
    # Loading SPANISH POS TAGGER
    logging.error('Loading POS TAGGER') 
    tagger_es = pickle.load(open( "tmp/POS_tagger.p", "rb" ) ).tag

    # Loading SPANISH CHUNK TAGGER
    logging.error('Loading CHUNK TAGGER')
    chunker_es = pickle.load(open( "tmp/CHUNK_tagger.p", "rb" ) ).parse 
    
    #spanish sent token
    sent_es_token = nltk.data.load('tokenizers/punkt/spanish.pickle')
    
    news = [dict(news_db.get(post)) for post in news_db]

    # Order news by date
    ordered_news = sorted(news,key=lambda new: new['published'])
    last_date = ''
    index = 0 
    mssg_id = 0 
    len_query = len(ordered_news)
    print len_query
    
    for post in ordered_news:
               
        # Group articles in a 7-day time window
        if index ==0: # first time
            last_date = post['published']
            index+=1
    
        if (post['published'] - last_date).days < 5:
            if post['cleaned_summary'] != None:
                time_slices[last_date].append([ post['cleaned_summary'], post['id']]) 
    
                sys.stderr.write('ids:%d [%f]\r' % (mssg_id,float(mssg_id*100)/float(len_query))) 
                mssg_id+=1              
        else: # New timeslice
            
            texts = defaultdict(list)
            # Get topics for the previous timeslice
            objects_ids = []
            for text,id in time_slices[last_date]:
                try:
                    lang, prob = langid.classify(text)       
                    # Most probable that weird languages are part of the main language            
                    if lang not in languages:
                        lang = user_language
                except TypeError:
                    continue                           
                words = []
                if lang == 'es':
                    sent_tokenizer = sent_es_token.tokenize                  
                else:
                    continue
                for sentence in sent_tokenizer(text):
                    tokens = [token.lower() for token in TreebankWordTokenizer().tokenize(sentence)]
                    words.extend(tokens)
                
                objects_ids.append(id)    
                texts[lang].append(words)

            # The tokens of the languages will be merged
            texts_tokens = []
            
            for lang in texts:
                # So far only ES, EN and DA
                if lang not in languages: continue
                if lang == 'es':
                    tagger = tagger_es
                    chunker = chunker_es                       
                else:
                    # Pre-trained English tagger and chunker
                    continue
    
                #print 'POSING...'
                nouns = ['NN','NNP','NNPS','NNS','NC','N_N']
                #nouns = ['NN','NNP','NNPS','NNS','NC']
                for t in texts[lang]:
                    words = []
                    
                    pos_sentence = tagger(t)    
                    if lang == 'da':            
                    named_sentence = chunker(pos_sentence)   
                    for j in named_sentence:
                        if type(j) == nltk.tree.Tree:
                            #print j.leaves()
                            words.append(' '.join([i[0] for i in j.leaves() if len(i[0]) > 2 and len(i[0]) < 20]))
                        else:
                            if len(j[0]) <= 2 or len(j[0]) >= 20: continue                    
                            if j[0].lower().strip('.').encode('utf-8') in names:
                                words.append(j[0])
                                continue
                            if j[1] not in nouns: continue
                            if j[0].lower().strip('.').encode('utf-8') in stopwords.words(stop_langs[lang]):
                                continue 
                            if j[0].lower().strip('.').encode('utf-8') in time_tokens:
                                continue
                            words.append(j[0])
                            
                    texts_tokens.append(words)

            # Discard tokens that appear once 
            tokens = sum(texts_tokens, []) 
            lonely_tokens = set(word for word in set(tokens) if tokens.count(word) == 1)
            
            texts = []
            for text in texts_tokens:
                aux = []
                for word in text:
                    if word not in lonely_tokens:
                        aux.append(word)
                texts.append(aux)
    
            dictionary = corpora.Dictionary(texts)
    
            corpus = [dictionary.doc2bow(text) for text in texts] 
    
            tfidf = models.TfidfModel(corpus)
            corpus_tfidf = tfidf[corpus] 
            num_topics=7
            
            # If there are less news than the maximun number of topics
            if len([t for t in corpus_tfidf]) < num_topics:
                num_topics = len([t for t in corpus_tfidf])
            try:
                model = models.ldamodel.LdaModel(corpus_tfidf, id2word=dictionary, num_topics=num_topics)
            except:
                # Update new time_lice date
                last_date = post['published']
                if post['cleaned_summary'] != None:
                    time_slices[last_date].append([post['cleaned_summary'],post['id']])  
                sys.stderr.write('ids:%d [%f]\r' % (mssg_id,float(mssg_id*100)/float(len_query))) 
                mssg_id+=1                         
                continue
            
            topics_aux = []
            # At least, as many topics as documents
            #for i in range(len(time_slices[last_date])):
            for i in range(num_topics):
                try:
                    # Get all the words for the prob distribution
                    topic = model.show_topic(i,len(dictionary))
                    #topic_dist[len(topic_dist)] = topic
                    topics_aux.append(topic)
                except IndexError:
                    sys.stderr.write('ids:%d [%f]\r' % (mssg_id,float(mssg_id*100)/float(len_query))) 
                    mssg_id+=1              
                    continue
            
            def hellinger_score(p, q):
                    
                i = [t[0] for t in sorted(p,key=lambda word: word[1])]
                j = [t[0] for t in sorted(q,key=lambda word: word[1])]
    
                return 1-np.sqrt(np.sum((np.sqrt(i) - np.sqrt(j)) ** 2)) /  np.sqrt(2)                
    
            # Check similarity between topics 
            answer = defaultdict(list)
            topic_discarded = set()
            discarded_dict = {}  
            index_1 = 0 
            for topic_a in topics_aux: 
                index_2 = 0
                for topic_b in topics_aux:
                    if index_1!=index_2:
                        
                        score = hellinger_score(topic_a, topic_b)
                        answer[index_1].append({index_2:score})
                            
                    index_2+=1
                index_1+=1
            
            topics_grouped = {}
            if len(answer)!=0:
                G=nx.Graph()
                for i in answer:
                    order_set = sorted(answer[i], key=lambda x: x.items()[0][1], reverse=True)
                    for j in order_set:
                        if j.values()[0]>0.7:
                            G.add_edge(j.keys()[0],i)
                        else:
                            G.add_edge(i,i)
                            break
                
                components = nx.connected_components(G)
                index = 0
                
                grouped_topic_dist = {}
                grouped_topic_words = {}
                
                index = 0
                for i in components:
                    for topic_id in i:
                        grouped_topic_dist[topic_id] = len(topic_dist)
                        
                    topic_dist[len(topic_dist)] = topics_aux[i[0]]
                    
                    grouped_topic_words[index] = topics_aux[i[0]]
                    
                    index+=1
            else:
                print len(topics_aux)
                if len(topics_aux)>1:
                    print topics_aux
                    quit()
                #quit()
                grouped_topic_dist = {}
                grouped_topic_words = {}
                
                index = 0        
                for topic in topics_aux:
                    topic_dist[len(topic_dist)] = topic
                    grouped_topic_dist[index] = len(topic_dist)
                    grouped_topic_words[index]=topics_aux    
                    index+=1           

            ################################################
            ################################################   
            #Once we have the topics, assign them to the news
            ################################################
            ################################################

            news = {}
            index = 0
            elements_dist = [t for t in model[corpus_tfidf]]
    
            for text,id_new in time_slices[last_date]:
                
                # REPASAR ESTO: CASO EN EL QUE EL TEXTO SEA VACIO Y POR TANTO NO SE HAYA
                # ENCONtRADO TOPICO PARA EL. 
                
                if len(elements_dist[index]) == 0:
                    news_db.save({"_id":id_new,"Topic_id": -1})
                else:
                    topic_assign = sorted(elements_dist[index],key=lambda t:t[1],reverse=True)[0]
                        
                    news_db.save({"_id":id_new,"Topic_id":grouped_topic_dist[topic_assign[0]]})
                        
                index+=1
            ################################################
            ################################################
                        
            topic_slices[last_date] = grouped_topic_words.values()
            # Update new time_lice date
            last_date = post['published']
            if post['cleaned_summary'] != None:
                time_slices[last_date].append([post['cleaned_summary'],post['id']]) 
    
            sys.stderr.write('ids:%d [%f]\r' % (mssg_id,float(mssg_id*100)/float(len_query))) 
            mssg_id+=1  
                
    pickle.dump(topic_dist, open( "tmp/topic_dist_test_5_days.p", "wb" ) )
    pickle.dump(topic_slices, open( "tmp/topic_slices_test_5_days.p", "wb" ) )
    fin = time.time()
    print 'Time consumed: %f' % ((float(fin)-float(ini))/60/60) 



if __name__ == '__main__':
	main()