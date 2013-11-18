#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
The aim of the script is to build the network of users of meneame, defined
as follows:
    - Each vertex is a user that has commented in one of the articles we
    analyzed. Each vertex has an attribute, "comments", that represents
    the total number of comments an user has posted
    - There is an edge between two users if they posted in the same article.
    Each edge has a weight representing the number of articles in which they
    posted together.
After the network has been created, it is pickled for subsequent analysis.
"""
import igraph as ig
import couchdb
import sys
import itertools
import collections


def create_graph(vertices, edges):
    """Return the graph object, given the edges and vertices collections.

    Keyword arguments:
    vertices -- collection of vertices, where each element is in the format
        username: number_of_comments
    edges -- collection of edges, where each element is in the format
        (username1, username2): weight, where the weight is the number
        of articles in which the two users have commented together

    The creation of the graph is done only on the final step of the
    function, due to the way igraph deals with the edges.
    Infact, building first the graph and then the edges would result in a
    very inefficient code, as the edges are re-indexed every time a new edge
    is added.
    """
    usernames = vertices.keys()
    comments = vertices.values()
    users_dic = {name: idx for (idx, name) in enumerate(usernames)}
    n_users = len(usernames)

    edges_list = [(users_dic[el1],
                   users_dic[el2]) for (el1, el2) in edges.keys()]
    weights_list = edges.values()

    vertex_attrs = {'name': usernames, 'comments': comments}
    edge_attrs = {'weight': weights_list}
    return ig.Graph(n=n_users, edges=edges_list, vertex_attrs=vertex_attrs,
                 edge_attrs=edge_attrs)


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
