import requests
from bs4 import BeautifulSoup
from Article import Article
from Comment import Comment
import re
import datetime

class Scraper(object):
    
    def __init__(self, base_url):
        self.base_url = base_url
        self.soup = None
    
    def scrap(self):
        
        articles = []
        
        for page in range(1, 2):
            url = self.base_url + '?page=%d' % page
            r = requests.get(url)
            self.soup = BeautifulSoup(r.text)
            
            data = self.soup.find_all('div', {'class' : 'news-body'})
            for article in data:
                articles.append(self.build_article(article))
            
            # save to file
            self.meneame_to_json(page, articles)
        
    def meneame_to_json(self, page, articles):
        f = open(self.time_stamped('meneame_%s.csv' % page), 'w')
        for article in articles:
            f.write(article.to_csv() + '\n')
        f.close()
        
    def time_stamped(self, fname, fmt='%Y-%m-%d-%H-%M-%S_{fname}'):
        return datetime.datetime.now().strftime(fmt).format(fname=fname)
            
    def build_article(self, data):
        
        article = Article()
        
        article.votes = int(data.find('div', {'class' : 'votes'}).a.string)
        article.clicks = data.find('div', {'class': 'clics'}).string
        
        # get the number of clicks
        r = re.match('\s*(\d*)\s.*', article.clicks)
        if r is not None:
            article.clicks = int(r.group(1))
            
        article.title = data.h2.a.string
        article.url = data.h2.a['href']
        new = data.find('div', {'class': 'news-submitted'})
        article.user = new.a['href']
        
        # get the username
        r = re.match('\/user\/(.*)', article.user)
        if r is not None:
            article.user = r.group(1)
        
        article.description = data.contents[8]
        
        story = data.find('span', {'class': 'comments-counter'}).a['href']
        article.story_url = self.base_url + story
        
        comment_counter = data.find('span', {'class': 'counter'})
        article.comment_counter = int(comment_counter.string)
        
        #article.comments = self.article_comments(article.story_url)
        
        return article
    8
    def build_comment(self, data):
        comment = Comment()
        comment.id = data.find('div', {'class': 'comment-body'})['id']
        comment.url = data.find('div', {'class': 'comment-body'}).a['href']
        comment.number = data.find('div', {'class': 'comment-body'}).a.strong.string
        comment.comment = data.find('div', {'class': 'comment-body'}).contents
        info = data.find('div', {'class': 'comment-info'}).a
        if info != None and 'href' in info: 
            comment.author = info['href']
        return comment
        
    def article_comments(self, url):
        
        comments = []
        
        r = requests.get(url)
        soup = BeautifulSoup(r.text)
        comments_list = soup.find('ol', {'class': 'comments-list'}).find_all('li')
        for comment in comments_list:
            comments.append(self.build_comment(comment))
            
        return comments
      
scraper = Scraper('http://www.meneame.net')
scraper.scrap()