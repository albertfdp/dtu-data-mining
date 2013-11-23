#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This script aim is two-fold:

* Update the database with a cleaned version of the content of the
    articles comments, with all the html tags stripped;
* Update the database with a dictionary of commenters for each article.
    In particular, the keys of the dictionary will be commenters, while the
    values will be the number of comments.

Those two operations are necessary for the subsequent analysis.
"""

import couchdb
import logging
import sys
from bs4 import BeautifulSoup


def strip_html_tags(html):
    """Strip out all html tags from the input text.

        :param html: input html string
        :returns: the input string stripped of all html tags
    """
    return ''.join(BeautifulSoup(html).findAll(text=True))


def test_strip_html_tags():
    """Test for the strip_html_tags function."""
    text = list()
    stripped = list()

    text.append("This is a text without HTML")
    stripped.append("This is a text without HTML")

    text.append("This text contains <b>one</b> tag")
    stripped.append("This text contains one tag")

    text.append("This text <i>contains</i> <b>two</b> tags")
    stripped.append("This text contains two tags")

    text.append("This <br>text <i>contains</i> <b><i>multiple</i></b> tags")
    stripped.append("This text contains multiple tags")

    for i in range(len(text)):
        assert strip_html_tags(text[i]) == stripped[i]


def main():
    """Main function. """
    logging.basicConfig(filename='cleaner.log',
                        level=logging.DEBUG, filemode='w')
    logging.basicConfig(format='%(asctime)s %(message)s')

    #Connection with the database
    try:
        couch = couchdb.Server()
        news_db = couch['meneame']
    except couchdb.ResourceNotFound, err:
        logging.exception("Connection error with the database! \n")
        logging.exception(err)
        sys.exit(1)

    logging.info('Connection to the databases estabilished')

    for element in news_db:

        logging.info('Considering article ' + element)
        news = dict(news_db.get(element))

        comments = news['comments']
        commenters = dict()

        for comment in comments:
            user = comment['user']

            #Adding to the commenters list
            commenters.setdefault(user, 0)
            commenters[user] = commenters[user] + 1

            #Adding the cleaned version of the comment
            cleaned_comment = strip_html_tags(comment['summary'])
            comment['cleaned_summary'] = cleaned_comment

        news['commenters'] = commenters
        news_db.save(news)


if __name__ == '__main__':
    main()
