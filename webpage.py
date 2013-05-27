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
        for a in soup.find_all('a', href = True):
            href = a.get('href').encode('utf8')         # Note: deal with Chinese link
            if urlparse(href).scheme == '':             # lack of scheme (relative url)
                href = urljoin(self.url, href)
            urlset.add(href)
        return urlset



