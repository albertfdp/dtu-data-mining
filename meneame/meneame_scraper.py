import argparse
import logging
import requests
from bs4 import BeautifulSoup
import re
import json
import feedparser

MENEAME_BASE_URL = "http://www.meneame.net"
MENEAME_COMMENT_RSS_URL = MENEAME_BASE_URL + "/comments_rss2.php"

class CommandError(Exception):
    """
        Thrown when the user has made a mistake in the command line
    """

def extract_meneame_id(page):
    
    meneame_news_ids = []
    
    soup = BeautifulSoup(page)
    news = soup.find_all('div', {'class' : 'news-body'})
    for new in news:
        votes_id = new.find('div', {'class': 'votes'}).a['id']
        r = re.match('a-votes-(\d*)', votes_id)
        if r is not None:
            meneame_news_ids.append(int(r.group(1)))
            
    return meneame_news_ids

def scrap_meneame_new(new_id):
    logging.debug('scrapping new %d' % new_id)
    
    r = requests.get(MENEAME_COMMENT_RSS_URL, params = {'id': new_id})
    meneame_new = feedparser.parse(r.text)
    
    time_parsed = meneame_new.feed.published
    
    for meneame_comment in meneame_new.entries:
        comment = {}
        comment['order'] = meneame_comment['meneame_order']
        comment['karma'] = meneame_comment['meneame_karma']
        comment['user'] = meneame_comment['meneame_user']
        comment['votes'] = meneame_comment['meneame_votes']
        comment['id'] = meneame_comment['meneame_comment_id']
        comment['published'] = meneame_comment.published
        comment['summary'] = meneame_comment.summary
        print comment
    
    #meneame_new_xml = r.text
    #print meneame_new_xml

def scrap_meneame_news_ids(time='year', start_page=1, max_page=100000):
    logging.debug('starting to scrap from %s at page %d for news in the timeframe \"%s\"' % (MENEAME_BASE_URL, start_page, time))
    
    meneame_news_ids = []
    
    for page in range(start_page, max_page): # TODO: fix
        r = requests.get(MENEAME_BASE_URL, params = {'page': page})
        meneame_news_ids = meneame_news_ids + extract_meneame_id(r.text)
        
    return meneame_news_ids

def save_meneame_news_ids(filename, time, news_ids):
    doc = {'time': time, 'ids': news_ids}
    with open(filename, 'w') as outputfile:
        json.dump(doc, outputfile)
    
def main():
    try:
        parser = argparse.ArgumentParser(description='Scrap meneame.net news and output them into a couchdb file')
        parser.add_argument('-t', '--time', choices=['year', 'all'], default='year', help='the timeframe to download')
        parser.add_argument('-s', '--start', type=int, default=1, help='the page to start with')
        parser.add_argument('-m', '--max', type=int, default=100000, help='maximum number of pages')
        parser.add_argument('-f', '--filename', default='meneame_news_ids.json', help='file to store the ids of the news')
        parser.add_argument('--verbose', action='store_true', help='print debugging info')
        parser.add_argument('--version', action='version', version='%(prog)s 1.0')
    
        args = parser.parse_args()
        
        if args.verbose:
            logging.basicConfig(level=logging.DEBUG)
        
        meneame_news_ids = scrap_meneame_news_ids(args.time, args.start, args.max)
        
        if args.filename:
            save_meneame_news_ids(args.filename, args.time, meneame_news_ids)
        
        for meneame_new_id in meneame_news_ids:
            scrap_meneame_new(meneame_new_id)
        
    except CommandError as error:
        print error

if __name__ == '__main__':
    main()