#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module contains the necessary functions for cleaning the articles.
"""

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
