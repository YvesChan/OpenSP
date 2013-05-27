#-*- coding:utf-8 -*-

import argparse
from urlparse import urlparse

_default = dict(
    log_file = 'spider.log',
    db_file = 'spider.db',
    log_level = 3,
    thread_num = 8,
    interval = 10
)

def check_int(num):
    errbuf = "Must be a positive integer."
    try:
        value = int(num)
    except ValueError:
        raise argparse.ArgumentTypeError(errbuf)
    if value < 1:
        raise argparse.ArgumentTypeError(errbuf)
    else:
        return value

def check_url(s):
    if urlparse(s).scheme not in ['http', 'https', 'ftp']:
        s = 'http://' + s
    return s

parser = argparse.ArgumentParser(description = 'OpenSP : An open source spider program')

parser.add_argument('-u', type=check_url, required=True, metavar='URL', dest='url', help='Specify the begin url')

parser.add_argument('-d', type=check_int, required=True, metavar='DEPTH', dest='depth', help='Specify the crawling depth')

parser.add_argument('--logfile', type=str, metavar='FILE', default=_default['log_file'], dest='log_file',
                   help='The log file path, Default: %s' % _default['log_file'])

parser.add_argument('--loglevel', type=int, choices=[1, 2, 3, 4, 5], default=_default['log_level'], dest='log_level',
                   help='The level of logging details. Larger number record more details. Default:%d' % _default['log_level'])

parser.add_argument('--thread', type=check_int, metavar='NUM', default=_default['thread_num'], dest='thread_num',
                   help='The amount of threads. Default:%d' % _default['thread_num'])

parser.add_argument('--dbfile', type=str, metavar='FILE', default=_default['db_file'], dest='db_file',
                   help='The SQLite file path. Default:%s' % _default['db_file'])

parser.add_argument('--interval', type=check_int, metavar='INTERVAL', default=_default['interval'], dest='interval',
                    help='print progress rate\'s interval. Default:%ds' % _default['interval'])