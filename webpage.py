#-*- coding:utf-8 -*-

import requests
import logging
import traceback
from datetime import datetime
from urlparse import urlparse, urljoin

from bs4 import BeautifulSoup

log = logging.getLogger('Main.webpage')

class WebPage(object):
    """fetch and store webpage source code"""
    def __init__(self, url):
        super(WebPage, self).__init__()
        self.url = url
        self.domain = urlparse(url).hostname            # get url's domain name
        self.html = None        # source code
        self.timestamp = None
        self.header = {         # initial header
            'Accept' : 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Charset' : 'GBK,utf-8;q=0.7,*;q=0.3',
            'Accept-Encoding' : 'gzip,deflate,sdch',
            'Accept-Language' : 'en-US,en;q=0.8',
            'Connection': 'keep-alive',
            'User-Agent' : 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.31 (KHTML, like Gecko) Chrome/26.0.1410.63 Safari/537.31',
            'Referer' : self.url,
        }

    def fetch(self, retry = 2):
        '''fetch webpage source'''
        try:
            response = requests.get(self.url, headers = self.header, timeout = 10)
            if response.status_code == 200 and 'html' in response.headers['content-type']:      # auto redirection(301, 302) & only save html 
                self.html = response.text       # unicode encoding
                self.timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                return True
            else:
                log.warning('Page not available. \nURL: %s ; Status Code: %d\n' % (response.url, response.status_code))
        except Exception, e:
            if retry > 0:
                self.fetch(retry - 1)
            else:
                log.info('\nURL: %s\n' % self.url + traceback.format_exc())
            return False

    def get_data(self):
        return self.url, self.timestamp, self.domain, self.html

    def set_header(self, **kargs):
        self.header.update(kargs)

    def get_link(self):
        '''get unique links from html and process unstandard url, return a set'''
        soup = BeautifulSoup(self.html)
        urlset = set()
        print("extending links from %s" % self.url)
        for a in soup.find_all('a', href = True):
            url = a.get('href').encode('utf8')         # Note: deal with Chinese link
            standard_url = self.filter_url(url)
            if standard_url is not None:
                urlset.add(standard_url)
            else:
                log.info('get_link() : drop link %s' % url)
        return urlset

    def filter_url(self, url, key = None):
        '''check the url extended from webpage, transform it into standard format or drop it'''
        res = urlparse(url)
        accept_type = {'htm', 'html', 'shtml', 'xhtml', 'jsp', 'php', 'asp', 'aspx', ''}
        # Check link's type. First get the url's filename(no slash), then judge it's type
        # Since we can't predict whether this url is a webpage of directory path(e.g. www.foo.com/bar/abc or www.foo.com/bar/abc/), so '' is acceptable
        if res.scheme not in {'http', 'https', ''}:     # other scheme(e.g. javascript, mailto...) is filtered
            return None
        if res.scheme == '':
            url = urljoin(self.url, url) 
        path = res.path.split('/')[-1]      # judge directory , accept '/abc/def' or '/abc/def/'
        if '.' not in path:                 # may be dir
            if len(path) > 10:
                return None
        if path.split('.')[-1] not in accept_type:        # get file type
            return None 
        if key is not None and key not in url:
            return None
        return url



