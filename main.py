#!/usr/bin/env python
#-*- coding:utf-8 -*-

import logging
import time
from datetime import datetime
from threading import Thread

from getoptions import parser
from spider import Spider


def logconf(logfile, loglevel):
    '''configure logging module'''
    logger = logging.getLogger('Main')
    level = {       # the higher level, the more information output
        1 : logging.CRITICAL,
        2 : logging.ERROR,
        3 : logging.WARNING,
        4 : logging.INFO,
        5 : logging.DEBUG
    }
    format = logging.Formatter('%(asctime)s %(threadName)-10s %(levelname)-8s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    try:
        file_handler = logging.FileHandler(logfile)
    except IOError, e:
        print('Fail to create log file %s : Permission Deny' % logfile)
        return false
    else:
        file_handler.setFormatter(format)
        logger.addHandler(file_handler)
        logger.setLevel(level.get(loglevel))
        return True

class printProgress(Thread):
    '''subthread, print progress info every (interval) s'''

    def __init__(self, spider, interval):
        Thread.__init__(self)
        self.name = 'printProgress'
        self.begin_time = datetime.now()
        self.interval = interval
        self.spider = spider
        self.daemon = True              # exit with the main Thread

    def run(self):
        while self.spider.status:
            print '\n-------------------------------------------'
            print 'CurrentDepth : %d' % self.spider.currentDepth
            print 'Already visited %d Links' % len(self.spider.visited_list)
            print '%d tasks remaining in task_list.' % len(self.spider.prefetch_list)
            print '-------------------------------------------\n'   
            time.sleep(self.interval)

    def print_total_time(self):
        self.end_time = datetime.now()
        print('Begin time: %s' % self.begin_time)
        print('End time: %s' % self.end_time)
        print('Totally Spend %s  \n' % (self.end_time - self.begin_time))



if __name__ == '__main__':
    args = parser.parse_args()
    if not logconf(args.log_file, args.log_level):
        print('logger configure failed!')
    else:
        spider = Spider(args)
        printpro = printProgress(spider, args.interval)
        spider.start()
        printpro.start() 
        print("Misson complete")
        printpro.print_total_time()