# -*- coding: utf-8 -*-
"""
Created on Wed Oct 16 15:25:53 2013

@author: ferdinando
"""

import networkx as nx
import couchdb
import logging
import sys
import itertools

logging.basicConfig(filename='network_creator.log',level=logging.DEBUG, filemode='w')
logging.basicConfig(format='%(asctime)s %(message)s')


#Connection with the databases
try:
    couch = couchdb.Server()
    news_db = couch['meneame']
except Exception, err:
    logging.exception("Problem with retrieving the databases \n")
    logging.exception(err)
    sys.exit(1)

logging.info('Connection to the databases estabilished')


G = nx.Graph()


for item in  [dict(news_db.get(el))['commenters'] for el in news_db]:
    G.add_nodes_from(item)
    for entry in item:
        try:
            G.node[entry]['weight'] += item[entry]
        except:
            G.node[entry]['weight'] = item[entry]
        for source, target in itertools.combinations(item.keys(), 2):
            G.add_edge(source, target)
            try:
                G.edge[source][target]['weight'] += 1
            except:
                G.edge[source][target]['weight'] = 1


nx.write_gpickle(G,'network.pickle')
