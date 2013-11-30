# -*- coding: utf-8 -*-
"""
    scraper.py

    Module for scraping meneame stories
"""
from menestats.model import MeneameStory, MeneameComment
import requests
import logging
import feedparser
from bs4 import BeautifulSoup
import re
import os

MENEAME_BASE_URL = 'http://www.meneame.net'
MENEAME_TOP_STORIES_URL = MENEAME_BASE_URL + "/topstories.php"
MENEAME_COMMENTS_RSS_URL = MENEAME_BASE_URL + "/comments_rss2.php"


def extract_comments(sid, text):
    """
        Extracts comments from a XML string. The parsing is done
        using feedparser library.
    """
    parsed = feedparser.parse(text)

    published = parsed.feed.published

    comments = []
    for comment in parsed.entries:
        meneame_comment = MeneameComment(sid)
        meneame_comment.order = comment['meneame_order']
        meneame_comment.karma = comment['meneame_karma']
        meneame_comment.user = comment['meneame_user']
        meneame_comment.votes = comment['meneame_votes']
        meneame_comment.id = comment['meneame_comment_id']
        meneame_comment.published = comment.published
        meneame_comment.summary = comment.summary
        comments.append(meneame_comment)

    return published, comments


def scrap_comments(sid):
    """
        Request RSS page with the comments of a meneame story for a given
        sid (meneame story id).
    """
    params = {'id': int(sid)}
    req = requests.get(MENEAME_COMMENTS_RSS_URL, params=params)
    logging.info('Scrap comments %s ...', req.url)
    published, comments = extract_comments(sid, req.text)
    return published, comments


def scrap_page(time_range, page):
    """
        Scrap a single story from the specified URL.

        Returns a list of MeneameStory objects
    """
    params = {'page': page, 'range': time_range}
    req = requests.get(MENEAME_TOP_STORIES_URL, params=params)
    logging.debug('Scrap page %s', req.url)
    stories = extract_stories(req.text)
    return stories


def extract_stories(text):
    """
        Parses an HTML page and builds a list of MeneameStory
    """

    parsed_stories = []

    soup = BeautifulSoup(text)
    stories = soup.find_all('div', {'class': 'news-body'})

    for story in stories:
        # build a dict with all the relevant attributes
        meneame_story = MeneameStory()

        # number of votes
        id_temp = story.find('div', {'class': 'votes'})
        meneame_story.votes = int(id_temp.a.string)

        # extract the id
        id_regex = re.match(r'a-votes-(\d*)', id_temp.a['id'])
        if id_regex:
            meneame_story.id = int(id_regex.group(1))

        meneame_story.title = story.h2.a.string
        meneame_story.url = story.h2.a['href']

        # number of clicks
        clicks = story.find('div', {'class': 'clics'})
        clicks_regex = re.match(r'\s*(\d*)\s.*', clicks.string)
        try:
            if clicks_regex:
                meneame_story.clicks = int(clicks_regex.group(1))
        except ValueError:
            logging.error('Error reading clicks for story %s',
                          meneame_story.id)
            meneame_story.clicks = 0

        # extract the user id
        user_a = story.find('a', {'class': 'tooltip'})
        user_regex = re.match(r'\/user\/(.*)', user_a['href'])
        if user_regex:
            meneame_story.author = user_regex.group(1)

        # extract description
        try:
            meneame_story.description = story.contents[8]
        except IndexError:
            logging.error('Error reading description for story %s',
                          meneame_story.id)
            meneame_story.description = story.contents

        parsed_stories.append(meneame_story)
    return parsed_stories


def test_extract_stories():
    """
        Test for the extract_stories function.
    """

    test_data = open(os.path.join(os.path.dirname(__file__),
                     'test_data.html')).read()
    stories = extract_stories(test_data)

    # assert there are 15 stories parsed
    assert len(stories) is 15

    # assert that each story has id, author, description, ....
    story = stories[0]
    assert story.id == 2066791
    assert story.title == u"La Policía intenta cerrar Canal 9 \
    y los trabajadores lo impiden. #RTVVnoestanca "
    assert story.votes == 711
    assert story.clicks == 2848
    assert story.url == u"https://www.youtube.com/watch?v=c6mX4owi1fY"
    assert story.author == u"ninyobolsa"
    assert story.description == u"""  Los trabajadores de RTVV,\
encerrados en el Estudio 4 de Canal9 en la que parece ser la úl\
tima noche de emisión de la cadena valenciana, se aglutinan en \
la sala del control central para impedir la entrada de los agen\
tes de Policía que pretenden cortar el cable que emite las imág\
enes, y lo logran. Relacionada:"""


def test_extract_comments():
    """
        Test for the extract_comments function.
    """
    test_data = open(os.path.join(
                     os.path.dirname(__file__), 'test_comments.xml')).read()
    published, comments = extract_comments(2067716, test_data)
    assert len(comments) is 77
    assert published == u'Sat, 30 Nov 2013 00:31:00 +0000'
    comment = comments[0]
    assert comment.order == u'77'
    assert comment.karma == u'18'
    assert comment.user == u'Lucer'
    assert comment.published == u'Sat, 30 Nov 2013 00:31:00 +0000'
    assert comment.id == u'13918274'
