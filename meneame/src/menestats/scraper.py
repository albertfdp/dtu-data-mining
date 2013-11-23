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
    logging.info('Scrap comments %s ...' , req.url)
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
        if clicks_regex:
            meneame_story.clicks = int(clicks_regex.group(1))

        # extract the user id
        user_a = story.find('a', {'class': 'tooltip'})
        user_regex = re.match(r'\/user\/(.*)', user_a['href'])
        if user_regex:
            meneame_story.author = user_regex.group(1)

        # extract description
        meneame_story.description = story.contents[8]

        parsed_stories.append(meneame_story)
    return parsed_stories
