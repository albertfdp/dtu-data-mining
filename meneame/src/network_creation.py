#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
The aim of the script is to build the network of users of meneame, defined
as follows:

* Each vertex is a user that has commented in one of the articles we\
    analyzed. Each *vertex* has an attribute, "comments", that represents\
    the total number of comments an user has posted;
* There is an *edge* between two users if they posted in the same article.\
    Each edge has a weight representing the number of articles in which they\
    posted together.

After the network has been created, it is pickled for subsequent analysis.
"""

#import igraph as ig
import couchdb
import sys
import itertools
import collections
from network.network import create_graph


def main():
    """ Main function. """
    #Connection with the database
    try:
        couch = couchdb.Server()
        news_db = couch['meneame']
    except couchdb.ResourceNotFound:
        print "Connection error with the database!"
        sys.exit(1)

    vertices_g = collections.Counter()
    edges_g = collections.Counter()

    #Populating vertices and edges collections
    for article in news_db:
        item = dict(news_db.get(article))['commenters']
        vertices_g.update(**item)
        edges_g.update(itertools.combinations(item.keys(), 2))

    graph = create_graph(vertices_g, edges_g)
    graph.simplify(combine_edges='sum')

    graph.write_pickle('meneame_network.pickle')

if __name__ == '__main__':
    main()
