# -*- coding: utf-8 -*-
"""
Created on Wed Oct 16 15:25:53 2013

@author: ferdinando
"""
import igraph as ig
import couchdb
import logging
import sys
import itertools
import collections
import matplotlib.pyplot as plt

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


g = ig.Graph()

#Creating vertices and edges collections
vertices = collections.Counter()
edges = collections.Counter()

count = 0
for article in news_db:
    count+=1
    if count == 500: #for testing!!!
        break
    item = dict(news_db.get(article))['commenters']            
    vertices.update(**item)
    edges.update(itertools.combinations(item.keys(), 2))


#Creating the graph
#we need to do all of this for performances reasons
# if we update the edges very often, it will be very inefficient, because
# the edges are indexed, and the indexed is done from the beginning every 
# edges list update

usernames = vertices.keys()    
comments = vertices.values()
users_dic = { name: idx for (idx,name) in enumerate(usernames)}
n_users = len(usernames)

    
edges_list = [(users_dic[el1],users_dic[el2]) for (el1,el2) in edges.keys()]
weights_list = edges.values()
n_edges = len(edges_list)

vertex_attrs = {'name':usernames, 'comments':comments}
edge_attrs={'weight': weights_list}
g = ig.Graph(n=n_users, edges=edges_list, vertex_attrs=vertex_attrs,
             edge_attrs=edge_attrs)
             

"""
    Constructs a graph from scratch.
    
    @keyword n: the number of vertices. Can be omitted, the default is
      zero.
    @keyword edges: the edge list where every list item is a pair of
      integers. If any of the integers is larger than M{n-1}, the number
      of vertices is adjusted accordingly.
    @keyword directed: whether the graph should be directed
    @keyword graph_attrs: the attributes of the graph as a dictionary.
    @keyword vertex_attrs: the attributes of the vertices as a dictionary.
      Every dictionary value must be an iterable with exactly M{n} items.
    @keyword edge_attrs: the attributes of the edges as a dictionary. Every
      dictionary value must be an iterable with exactly M{m} items where
      M{m} is the number of edges.

"""
#max, min, average, variance?

print "Number of users: ", n_users
print "Number of connections: ", n_edges
print "Max. number of comments: ", max(comments)
print "Max. number of articles together: ", max(weights_list)


degree_sequence = sorted(g.indegree(), reverse=True)
#plt.yscale('log')
#plt.plot(degree_sequence,'b-')
plt.figure()
plt.hist(degree_sequence,len(g.indegree()),log=True)
plt.figure()
xs, ys = zip(*[(left, count) for left, _, count in g.degree_distribution().bins()])
plt.bar(xs, ys)
plt.show()
