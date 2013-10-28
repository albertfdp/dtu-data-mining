# -*- coding: utf-8 -*-
"""

"""

import sys

from datetime import date, datetime
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

import logging

from numpy import zeros, array
from math import sqrt, log

def main():

    topic_ids = pickle.load(open( "tmp/topic_dist_test_5_days.p", "rb" ) )
    topic_slices = pickle.load(open( "tmp/topic_slices_test_5_days.p", "rb" ) )
    
    topic_words = {}
     
    for i in topic_ids:
        
        topic_words[i] = topic_ids[i][:20]
        
    ini = time.time()
    
    # Order emails by date
    ordered_slices = sorted(topic_slices.items(),key=lambda email: email[0])

    aux_ordered_slices = []
    for t_slice in ordered_slices:
        t = [t_slice[0].year,t_slice[0].month,t_slice[0].day,t_slice[0].hour,t_slice[0].minute,t_slice[0].second]
        
        topics_ids = []
        for topic_s in t_slice[1]:
            if len(topic_s)==1 and type(topic_s[0]) ==type([]):
                aux = topic_s[0]
            else:
                aux = topic_s
            topic_id = []
    
            for id,topic in topic_ids.items():
                if topic==aux:
                    topic_id.append([id,topic])

            if len(topic_id)==1:
                topic_id = topic_id[0]    
            topics_ids.append(topic_id)
        
        aux_ordered_slices.append({'date':t,'topics':topics_ids})
        
    index = 0
    topic_chain = defaultdict(list)
    topic_dist = {}
    chain_links = defaultdict(list)
      
    topic_dates = {}
    
    for date in ordered_slices:
        for topic_s in date[1]:
        
            if len(topic_s)==1 and type(topic_s[0]) ==type([]):
                aux = topic_s[0]
            else:
                aux = topic_s    
        
            topic_id = [id for id,topic in topic_ids.items() if topic==aux]
    
            topic_dates[topic_id[0]] = date[0]
            
    for date in ordered_slices:
        if index==0:
            index+=1
            continue
            
        slice_i = ordered_slices[index-1][1]  
        slice_j = ordered_slices[index][1]
    
        if len(slice_i)==1 and type(slice_i[0][0]) ==type([]):
            slice_i = slice_i[0]
        if len(slice_j)==1 and type(slice_j[0][0]) ==type([]):
            slice_j = slice_j[0]
    
        # Compare this topics with the previous time slice
        for j in slice_j:
            set_j = set([word[1] for word in j][:5])
            scores = []
            candidate = -1
            index_j = 0
            for i in slice_i:
                if i==j: continue
                # Jaccard similarity
                set_i = set([word[1] for word in i][:5])
                #compare set_i and set_j
                n = len(set_i.intersection(set_j))
                score_aux = n / float(len(set_i) + len(set_j) - n)                
                scores.append([score_aux,index_j])
                index_j+=1
       
            ordered_scores = sorted(scores,key=lambda score: score[0], reverse=True)     
            
            similarity_threshold = 0.30
            if len(ordered_scores) ==0: continue
            if ordered_scores[0][0] > similarity_threshold : 
                #Get topic ID
                topic_j_id = [id for id,topic in topic_ids.items() if topic==j] [0]
                topic_i_id = [id for id,topic in topic_ids.items() if topic==slice_i[ordered_scores[0][1]]] [0]
                
                if topic_i_id in topic_dist:
                    topic_chain[topic_dist[topic_i_id]].append([topic_i_id,topic_j_id])
                    chain_links[topic_i_id].extend([topic_j_id])
                    topic_dist[topic_j_id ] =  topic_dist[topic_i_id]
                else:
                    topic_dist[topic_i_id] = len(topic_chain)
                    topic_dist[topic_j_id ] =  len(topic_chain)
                    chain_links[topic_i_id].append(topic_j_id)
                    topic_chain[len(topic_chain)].append([topic_i_id,topic_j_id])
  
        index+=1

    def build_chain(key,value,chain_id):
        #if len(values)>0:
        if key in chain_links:
            if topic_dist[key] == chain_id:
                children = []
                for leaf in value:
                    values = build_chain(leaf,chain_links[leaf],chain_id)
                    children.extend(values)
                date = topic_dates[key]
                date =[date.year,date.month,date.day,date.hour,date.minute,date.second]  
                words = topic_words[key]              
                if len(children)>0:
                    return [{'name':key, 'children': children,'date':date,'words':words}]
                else: 
                    return [{'name':key,'date':date,'words':words}]
        else:
            # END
            date = topic_dates[key]
            date =[date.year,date.month,date.day,date.hour,date.minute,date.second]  
            words = topic_words[key]
            return [{'name':key,'date':date,'words':words}]
            
    chains = []
    print topic_chain
    print topic_dist
    for chain_id in topic_chain:
    
        key = topic_chain[chain_id][0][0]
        value = chain_links[key]
        print key
        print value
        print chain_id
        chain = build_chain(key,value,chain_id)
        print chain
        chains.append({'id':chain_id,'chain':chain,'start':chain[0]['date']})
        
    return {"topic_data": chains, "topic_words": topic_words,"topic_slices":aux_ordered_slices}

if __name__ == '__main__':
	main()