#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Module for scraping meneame stories
"""
from model import Story, Comment
import requests
import logging
import feedparser
from bs4 import BeautifulSoup
import re
import os


class ScraperFactory(object):
    """
    ScraperFactory: returns a Scraper implementation.

    """
    def factory(scrapper_type, base_url, stories_url, comments_url):
        """
            Returns a scrapper implementation.
        """
        if scrapper_type == 'meneame':
            return MeneameScraper(base_url, stories_url, comments_url)
    factory = staticmethod(factory)


class Scraper(object):
    """
        Abstract class Scraper which provides the basic methods for\
        scraping a social news website. It relies on subclasses for\
        specific methods.
    """

    def __init__(self, base_url, stories_url, comments_url):
        self.base_url = base_url
        self.stories_url = stories_url
        self.comments_url = comments_url

    @staticmethod
    def _scrap(url, params):
        """
            Private method. Should not be called directly. Reads an\
            HTTP page given a URL and some params.

                :param url: url to do an HTTP request.
                :param params: a dictionary of GET parameters.
        """
        try:
            logging.debug('requesting %s [%s]', url, params)
            req = requests.get(url, params=params)
        except requests.exceptions.ConnectionError:
            logging.error('error in the connection, skipping [params=%s]',
                          ','.join(params))
            return None
        if req.status_code is not 200:
            return None
        logging.debug('scrapped page %s ...', req.url)
        return req

    def scrap_page(self, params):
        """
            Requests a given HTTP page given the provided GET\
            parameters. Returns a list of Stories.

                :param params: a dictionary of GET parameters.

        """
        req = self._scrap(self.base_url + self.stories_url, params)
        if req is None:
            return None
        return self.extract_stories(req.text)

    def extract_stories(self, text):
        """
            Extract stories from the given HTTP text. Should be\
            implemented by subclasses of this Scraper class.

                :param text: a string read from an HTTP request.

        """
        pass

    def scrap_comments(self, params):
        """
            Requests a given HTTP page given the provided GET\
            parameters. Returns a list of Comments.

                :param params: a dictionary of GET parameters.

        """
        req = self._scrap(self.base_url + self.comments_url, params)
        if req is None:
            return None
        return self.extract_comments(params['id'], req.text)

    def extract_comments(self, sid, text):
        """
            Extract comments from the given HTTP text. Should be\
            implemented by subclasses of this Scraper class.

                :param sid: the id of the new of these comments.
                :param text: a string read from an HTTP request.

        """
        pass


class MeneameScraper(Scraper):
    """
        Implementation of the class Scraper. Provides methods for\
        obtaining meename stories and comments.
    """

    def __init__(self, base_url, stories_url, comments_url):
        super(MeneameScraper,
              self).__init__(base_url, stories_url, comments_url)

    def extract_stories(self, text):
        """
            Implementation of extract stories from the given \
            HTTP text. Returns a list of Stories.

                :param text: a string read from an HTTP request.

        """
        parsed_stories = []

        soup = BeautifulSoup(text)
        stories = soup.find_all('div', {'class': 'news-body'})

        for story in stories:
            # build a dict with all the relevant attributes
            meneame_story = Story()

            # number of votes
            id_temp = story.find('div', {'class': 'votes'})
            if id_temp:
                meneame_story.votes = int(id_temp.a.string)
            else:
                meneame_story.votes = 0

            try:
                # extract the id
                id_regex = re.match(r'a-votes-(\d*)', id_temp.a['id'])
                if id_regex:
                    meneame_story.id = int(id_regex.group(1))
            except AttributeError:
                logging.error('Could not read id for new, skipping ...')
                continue

            if story.h2 is not None:
                meneame_story.title = story.h2.a.string
                meneame_story.url = story.h2.a['href']
            else:
                meneame_story.title = ""
                meneame_story.url = ""

            # number of clicks
            clicks = story.find('div', {'class': 'clics'})
            if clicks is not None:
                clicks_regex = re.match(r'\s*(\d+)\s.*', clicks.string)
                if clicks_regex:
                    meneame_story.clicks = int(clicks_regex.group(1))
                else:
                    logging.error('Error reading clicks for story %s',
                                  meneame_story.id)
                    meneame_story.clicks = 0
            else:
                meneame_story.clicks = 0

            # extract the user id
            user_a = story.find('a', {'class': 'tooltip'})
            try:
                user_regex = re.match(r'\/user\/(.*)', user_a['href'])
                if user_regex:
                    meneame_story.author = user_regex.group(1)
            except (TypeError, ValueError):
                logging.error('Error reading user for story %s',
                              meneame_story.id)
                meneame_story.user = ""

            # extract description
            try:
                meneame_story.description = story.contents[8]
            except IndexError:
                logging.error('Error reading description for story %s',
                              meneame_story.id)
                meneame_story.description = " "

            parsed_stories.append(meneame_story)
        return parsed_stories

    def extract_comments(self, sid, text):
        """
        Extracts comments from a XML string. The parsing is done
        using feedparser library.

            :param sid: the id of the new.
            :param text: the RSS xml.

    """
        parsed = feedparser.parse(text)
        try:
            published = parsed.feed.published
        except AttributeError:
            published = parsed.feed.updated

        comments = []
        for comment in parsed.entries:
            meneame_comment = Comment(sid)
            meneame_comment.order = comment['meneame_order']
            meneame_comment.karma = comment['meneame_karma']
            meneame_comment.user = comment['meneame_user']
            meneame_comment.votes = comment['meneame_votes']
            meneame_comment.id = comment['meneame_comment_id']
            try:
                meneame_comment.published = comment.published
            except AttributeError:
                meneame_comment.published = comment.updated
            meneame_comment.summary = comment.summary
            comments.append(meneame_comment)

        return comments, published


def test_extract_stories():
    """
        Test for the extract_stories function.
    """

    meneame = ScraperFactory.factory('meneame',
                                     'http://www.meneame.net/',
                                     'topstories.php',
                                     'comments_rss2.php')

    test_data = open(os.path.join(os.path.dirname(__file__),
                     'test_data.html')).read()
    stories = meneame.extract_stories(test_data)

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


def test_extract_comments():
    """
        Test for the extract_comments function.
    """
    meneame = ScraperFactory.factory('meneame',
                                     'http://www.meneame.net/',
                                     'topstories.php',
                                     'comments_rss2.php')

    test_data = open(os.path.join(
                     os.path.dirname(__file__), 'test_comments.xml')).read()
    comments, published = meneame.extract_comments(2067716, test_data)
    assert len(comments) is 77
    assert published == u'Sat, 30 Nov 2013 00:31:00 +0000'
    comment = comments[0]
    assert comment.order == u'77'
    assert comment.karma == u'18'
    assert comment.user == u'Lucer'
    assert comment.published == u'Sat, 30 Nov 2013 00:31:00 +0000'
    assert comment.id == u'13918274'
