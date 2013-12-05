#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
The aim of this script is to analyze in various ways the meneame network.
"""
import igraph as ig
import os
import sys
from network.network import general_analysis, community_analysis
from network.network import save_degree_distribution
from network.network import save_weights_distribution

IMAGES_FOLDER = "images/"
NETWORK_FILE = "meneame_network.pickle"


def main():
    """Main function"""

    if not os.path.exists(NETWORK_FILE):
        print "Input network file is not present!"
        sys.exit(1)

    graph = ig.load(NETWORK_FILE)
    graph['name'] = 'meneame'

    general_analysis(graph)

    community_analysis(graph)

    save_degree_distribution(graph, IMAGES_FOLDER)
    save_weights_distribution(graph, IMAGES_FOLDER)


if __name__ == '__main__':
    main()
