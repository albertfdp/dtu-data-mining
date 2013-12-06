# -*- coding: utf-8 -*-
"""
    Python classes for that model the data used in the scripts.
"""
class Story(object):
    """
        A story
    """
    def __init__(self, sid=None, votes=None, clicks=None, title=None,
        url=None, author=None, description=None, published=None, comments=None):
        self.id = sid
        self.votes = votes
        self.clicks = clicks
        self.title = title
        self.url = url
        self.author = author
        self.description = description
        self.published = published
        self.comments = comments

    def to_dict(self):
        """
            Converts the class to a dictionary to be handled as a JSON
        """
        out = {}
        out['_id'] = str(self.id)
        out['votes'] = self.votes
        out['clicks'] = self.clicks
        out['title'] = self.title
        out['url'] = self.url
        out['author'] = self.author
        out['description'] = self.description
        out['published'] = self.published

        comments = []
        for comment in self.comments:
            comments.append(comment.to_dict())
        out['comments'] = comments

        return out


class Comment(object):
    """
        A comment
    """
    def __init__(self, story, order=None, karma=None, user=None,
        votes=None, cid=None, published=None, summary=None):
        self.story = story
        self.order = order
        self.karma = karma
        self.user = user
        self.votes = votes
        self.id = cid
        self.published = published
        self.summary = summary

    def to_dict(self):
        """
            Converts the class to a dictionary to be handled as a JSON
        """
        out = {}
        out['order'] = self.order
        out['karma'] = self.karma
        out['user'] = self.user
        out['votes'] = self.votes
        out['id'] = self.id
        out['published'] = self.published
        out['summary'] = self.summary
        return out
