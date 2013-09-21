import argparse
import logging
import requests
from bs4 import BeautifulSoup
import re
import json
import feedparser
import os.path

MENEAME_BASE_URL = "http://www.meneame.net"
MENEAME_TOP_STORIES_URL = MENEAME_BASE_URL + "/topstories.php"
MENEAME_COMMENT_RSS_URL = MENEAME_BASE_URL + "/comments_rss2.php"

MENEAME_DATASTORE_JSON = "meneos.json"
MENEAME_TEMP_COMMENT_DIR = "comments"

class CommandError(Exception):
    """
        Thrown when the user has made a mistake in the command line
    """

def extract_meneo(page):
    
    meneos = []
    
    soup = BeautifulSoup(page)
    news = soup.find_all('div', {'class' : 'news-body'})
    for new in news:
        meneo = {}
        
        votes_id = new.find('div', {'class': 'votes'})
        meneo['votes'] = votes_id.a.string
        r = re.match('a-votes-(\d*)', votes_id.a['id'])
        if r is not None:
            meneo['id'] = int(r.group(1))
            
        clicks = new.find('div', {'class': 'clics'}).string
        r = re.match('\s*(\d*)\s.*', clicks)
        if r is not None:
            meneo['clicks'] = int(r.group(1))
            
        meneo['title'] = new.h2.a.string
        meneo['url'] = new.h2.a['href']
        
        description = new.find('div', {'class': 'news-submitted'})
        user = new.a['href']
         
        # get the username
        r = re.match('\/user\/(.*)', user)
        if r is not None:
            meneo['author'] = r.group(1)
            
        meneo['description'] = new.contents[8]
        
        # removed due to performance issues
        #meneo = scrap_meneame_comments(meneo)
        
        meneos.append(meneo)
            
    return meneos

def download_comments(meneo):
    
    meneo_id = int(meneo['id'])
    
    if not os.path.exists(os.path.join(MENEAME_TEMP_COMMENT_DIR, 'meneo_%d_comments.xml' % meneo_id)):    
        logging.info('Downloading comments for %d' % meneo_id)
        
        r = requests.get(MENEAME_COMMENT_RSS_URL, params = {'id': meneo_id})
        with open(os.path.join(MENEAME_TEMP_COMMENT_DIR, 'meneo_%d_comments.xml' % meneo_id), 'w') as outputfile:
            outputfile.write(r.text.encode('utf-8'))

def scrap_meneame_comments(new):
    logging.info('scrapping new %d' % new['id'])
    
    r = requests.get(MENEAME_COMMENT_RSS_URL, params = {'id': new['id']})
    
    meneame_new = feedparser.parse(r.text)
    
    meneo = new
    meneo['published'] = meneame_new.feed.published
    
    meneame_comments = []
    for meneame_comment in meneame_new.entries:
        comment = {}
        comment['order'] = meneame_comment['meneame_order']
        comment['karma'] = meneame_comment['meneame_karma']
        comment['user'] = meneame_comment['meneame_user']
        comment['votes'] = meneame_comment['meneame_votes']
        comment['id'] = meneame_comment['meneame_comment_id']
        comment['published'] = meneame_comment.published
        comment['summary'] = meneame_comment.summary
        meneame_comments.append(comment)
        
    meneo['comments'] = meneame_comments
    
    return meneo

def scrap_meneos(timerange=1, page=1):
    logging.info('scraping page %d' % (page))
    
    r = requests.get(MENEAME_TOP_STORIES_URL, params = {'page': page, 'range': timerange})
    meneos = extract_meneo(r.text)
        
    return meneos

def save_meneos(meneos, filename=MENEAME_DATASTORE_JSON):
    """
        Read JSON file, merge meneos and store them
    """
    logging.info('saving meneos to file...')
    data = []
    if os.path.exists(filename):
        f = open(filename, 'r')
        data = json.load(f)
        f.close()
    
    root = {'meneame': {'meneos': []}}
    if data:
        for meneo in data['meneame']['meneos']:
            root['meneame']['meneos'] = root['meneame']['meneos'] + meneo
    for meneo in meneos:
        root['meneame']['meneos'].append(meneo)
        
    # delete duplicates
    root['meneame']['meneos'] = list({m['id']:m for m in root['meneame']['meneos']}.values())
    
    with open(filename, 'w') as outputfile:
        json.dump(root, outputfile)
    
def main():
    try:
        parser = argparse.ArgumentParser(description='Scrap meneame.net news and output them into a couchdb file')
        parser.add_argument('-t', '--time', choices=['24h', '48h', 'week', 'month', 'year', 'all'], default='year', help='the timeframe to download')
        parser.add_argument('-s', '--start', type=int, default=1, help='the page to start with')
        parser.add_argument('-m', '--max', type=int, default=100000, help='maximum number of pages')
        parser.add_argument('-f', '--filename', default='meneame_news_ids.json', help='file to store the ids of the news')
        parser.add_argument('--verbose', action='store_true', help='print debugging info')
        parser.add_argument('--version', action='version', version='%(prog)s 1.0')
    
        args = parser.parse_args()
        
        time_range = ['24h', '48h', 'week', 'month', 'year', 'all'].index(args.time)          
        
        if args.verbose:
            logging.basicConfig(level=logging.INFO)
            
        if not os.path.exists(MENEAME_TEMP_COMMENT_DIR):
            os.makedirs(MENEAME_TEMP_COMMENT_DIR)
        
        for i in range(args.start, args.max):
            meneos = scrap_meneos(time_range, i)
            #save_meneos(meneos)
            for meneo in meneos:
                download_comments(meneo)
        
        
    except CommandError as error:
        print error

if __name__ == '__main__':
    main()