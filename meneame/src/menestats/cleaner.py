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
