#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module contains the functions for the network analysis and creation.
"""

import igraph as ig
import collections
import matplotlib.pyplot as plt


def test_create_graph():
    """Testing function for create_graph()
    """
    vertices = {'user1': 12, 'user2': 8, 'user3': 7, 'user4': 4}
    vertices = collections.Counter(vertices)
    edges = {('user1', 'user2'): 23,
             ('user1', 'user3'): 12, ('user2', 'user4'): 11}
    edges = collections.Counter(edges)
    test_graph = create_graph(vertices, edges)

    for v in test_graph.vs:
        assert v['comments'] == vertices[v['name']]

    for e in test_graph.es:
        source = test_graph.vs[e.source]['name']
        target = test_graph.vs[e.target]['name']
        ed = tuple(sorted((source, target)))
        assert edges[ed] == e['weight']


def create_graph(vertices, edges):
    """Return the graph object, given the edges and vertices collections.

    :param vertices: collection of vertices, where each element is in the
        \format "username: number_of_comments"
    :param edges: collection of edges, where each element is in the format\
        (username1, username2): weight, where the weight is the number\
        of articles in which the two users have commented together\
    :returns: the igraph object

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


def save_degree_distribution(graph, image_folder):
    """Save the degree distribution of the input graph to file.

        :param graph: the input igraph object
        :image_folder: the path to the folder where to save the images
    """
    degree_dist = graph.degree_distribution()
    x = [el[0] for el in degree_dist.bins()]
    y = [el[2] for el in degree_dist.bins()]

    title = "Network Degree Distribution"
    xlabel = "Degree"
    ylabel = "Number of nodes"
    filename = graph['name'] + "_degree_distribution"
    save_log_histogram(x, y, title, xlabel, ylabel, filename, image_folder)


def save_weights_distribution(graph, image_folder):
    """Saves the weigth distribution to file.

        :param graph: the input igraph object
        :image_folder: the path to the folder where to save the images
    """
    weights = graph.es['weight']

    co = collections.Counter(weights)
    x = [el for el in co]
    y = [co[el] for el in co]

    title = "Weights distribution"
    xlabel = "Weight"
    ylabel = "Number of edges"
    filename = graph['name'] + "_weights_distribution"
    save_log_histogram(x, y, title, xlabel, ylabel, filename, image_folder)


def save_log_histogram(x, y, title, xlabel, ylabel, filename, image_folder):
    """Create a loglog histogram from the input x and y and saves it to\
    file. Each bin has an unitary size.

        :param x: bin positions
        :param y: count values
        :param title: title of the histogram
        :param xlabel: label of the x axis
        :param ylabel: label of the y axis
        :param filename: name of the saved file

    """
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.plot(x, y)
    ax.set_xscale('log')
    ax.set_yscale('log')
    plt.ylabel(ylabel)
    plt.xlabel(xlabel)
    plt.title(title)
    plt.savefig(image_folder + filename + '.png')
    plt.savefig(image_folder + filename + '.pdf')


def community_analysis(graph):
    """Analyze the communities of the input graph.

        :param graph: the input igraph object

    """
    print "\nCOMMUNITY ANALYSIS\n"

    communities = graph.community_infomap(edge_weights='weight',
                                          vertex_weights='comments',
                                          trials=10)
    print "Infomap  ", communities.summary()
    print "Sizes of communities: ", communities.sizes()
    single_community_analysis(communities)


def single_community_analysis(communities):
    """Analyze the communities found. The analysis is done only if more\
    than one community has been found.

        :param graph: the input VertexClustering object representing the\
        communities

    """
    n_comm = len(communities.sizes())
    if n_comm > 1:
        for idx in range(n_comm):
            print "\n COMMUNITY NUMBER ", idx, "\n"
            general_analysis(communities.subgraph(idx))


def general_analysis(graph):
    """Print to screen some basic information regarding the input graph.

        :param graph: the input igraph object

    """
    comments = graph.vs['comments']
    weights = graph.es['weight']

    print "GENERAL ANALYSIS\n"

    print "Number of users: ", graph.vcount()
    print "Number of links: ", graph.ecount()

    print "\nMax. number of comment per user: ", max(comments)
    print "Min. number of comment per user: ", min(comments)
    print "Average number of comments: ",
    print float(sum(comments)) / len(comments)

    print "\nMax. value of weight: ", max(weights)
    print "Min. value of weight: ", min(weights)
    print "Average weight: ", float(sum(weights)) / len(weights)

    print "\nClustering coefficient: ", graph.transitivity_undirected()

    components = graph.components()
    print "\nNumber of connected components: ", len(components.sizes())

    hist = graph.path_length_hist()
    lengths, paths = [[el[i] for el in list(hist.bins())] for i in [0, 2]]
    print "\nPath length distibution: "
    for i in range(len(lengths)):
        print paths[i], " paths with length ", lengths[i]

    print "\nAverage path length: ",
    splengths = sum([lengths[i] * paths[i] for i in range(len(lengths))])
    print splengths / sum(paths)
