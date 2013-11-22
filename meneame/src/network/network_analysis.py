#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
The aim of this script is to analyze in various ways the meneame network.
"""
import igraph as ig
import collections
import matplotlib.pyplot as plt

IMAGES_FOLDER = "images/"


def remove_weak_users(graph, min_val):
    """Return the filtered graph, considering only the vertices that have a\
    comments attribute bigger than min_val.

        :param graph: the input igraph object
        :param min_val: threshold value

    """
    gs = graph.vs.select(comments_gt=min_val)
    vertices_list = [el.index for el in gs]
    return graph.subgraph(vertices_list)


def remove_weak_edges(graph, min_val):
    """Return the filtered graph, considering only the edges that have a\
    weight attribute bigger than min_val.

        :param graph: the input igraph object
        :param min_val: threshold value

    """
    we = graph.es.select(weight_lt=min_val)
    weak_edges = [el.index for el in we]
    graph.delete_edges(weak_edges)
    return graph


def remove_lonely_nodes(graph):
    """Return the filtered graph, considering only the vertices that have\
    at least one neighbour.

        :param graph: the input igraph object

    """
    gs = graph.vs.select(_degree_gt=0)
    vertices_list = [el.index for el in gs]
    return graph.subgraph(vertices_list)


def save_degree_distribution(graph):
    """Save the degree distribution of the input graph to file.

        :param graph: the input igraph object

    """
    degree_dist = graph.degree_distribution()
    x = [el[0] for el in degree_dist.bins()]
    y = [el[2] for el in degree_dist.bins()]

    title = "Network Degree Distribution"
    xlabel = "Degree"
    ylabel = "Number of nodes"
    filename = graph['name'] + "_degree_distribution"
    save_log_histogram(x, y, title, xlabel, ylabel, filename)


def save_weights_distribution(graph):
    """Saves the weigth distribution to file.

        :param graph: the input igraph object

    """
    weights = graph.es['weight']

    co = collections.Counter(weights)
    x = [el for el in co]
    y = [co[el] for el in co]

    title = "Weights distribution"
    xlabel = "Weight"
    ylabel = "Number of edges"
    filename = graph['name'] + "_weights_distribution"
    save_log_histogram(x, y, title, xlabel, ylabel, filename)


def save_log_histogram(x, y, title, xlabel, ylabel, filename):
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
    plt.savefig(IMAGES_FOLDER + filename + '.png')
    plt.savefig(IMAGES_FOLDER + filename + '.pdf')


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
            print "Community number ", idx, "\n"
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
    print "Average number of comments: ", float(sum(comments)) / len(comments)

    print "\nMax. value of weight: ", max(weights)
    print "Min. value of weight: ", min(weights)
    print "Average weight: ", float(sum(weights)) / len(weights)

    print "\nClustering coefficient: ", graph.transitivity_undirected()

    components = graph.components()
    print "\nNumber of connected components: ", len(components.sizes())

    print "\nAverage path length: ", graph.average_path_length()


def main():
    """Main function"""
    graph = ig.load("meneame_network.pickle")
    graph['name'] = 'meneame'

    general_analysis(graph)

    community_analysis(graph)

    save_degree_distribution(graph)
    save_weights_distribution(graph)


if __name__ == '__main__':
    main()
