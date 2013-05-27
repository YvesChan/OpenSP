#-*- coding:utf-8 -*-

from threading import Thread, Lock
from Queue import Queue, Empty
import logging
import time
import traceback
from robotparser import RobotFileParser
from urlparse import urlparse

from webpage import WebPage
from database import Database

log = logging.getLogger('Main.spider')

class Spider(object):
    """actually a spider manager to control all the worker and maintain the msg queue"""
    def __init__(self, args):           # receive args from CLI
        self.depth = args.depth
        self.curr_depth = 1
        self.db = Database(args.db_file)
        self.visited_list = set()
        self.task_list = Queue(1000)            # for worker to fetch, try max_size = 1000
        self.prefetch_list = set()              # no repeat, disorder
        self.domain_list = dict()               # check robots.txt
        self.extend_list = set()                # cache for extend urls
        self.thread_num = args.thread_num
        self.running = 0                        # current running thread numbers (shared var)
        self.status = False
        self.pool = []
        self.lock = Lock()                      # use mutex to protect running
        self.prefetch_list.add(args.url)        # add init url

    def start(self):
        self.status = True
        print('Creating threads...')
        for i in xrange(self.thread_num):
            self.pool.append(Worker(self))      # init thread pool, create workers thread
        print('Starting crawling...')
        while self.curr_depth <= self.depth:
            pl_size = len(self.prefetch_list)
            while pl_size:
                url = self.prefetch_list.pop()  # get an url from prefetch_list
                pl_size -= 1
                self.task_list.put(url)         # add into task_list
                self.visited_list.add(url)      # add into visited_list as soon as possible
            while self.task_list.qsize():
                try:
                    time.sleep(5)
                except Exception, e:
                    print(str(e))
                    self.stop() 
            print('Depth %d finished!. Totally visited %d urls.\n' % (self.curr_depth, len(self.visited_list)))
            log.info('Depth %d finished!. Totally visited %d urls.\n' % (self.curr_depth, len(self.visited_list)))
            self.prefetch_list.update(self.extend_list)         # move urls from extend_list to prefetch_list
            self.extend_list.clear()
            self.curr_depth += 1
        if self.status:
            self.stop()

    def stop(self):
        '''stop the spider and its workers, close database'''
        self.status = False
        for worker in self.pool:
            worker.status = False
            worker.join()           # wait until this worker thread have terminated
        del self.pool[:]                 # delete all thread instances
        self.db.close()

    def check_robots(self, url):
        '''check the robots.txt in this url's domain'''
        hostname = urlparse(url).netloc
        if hostname not in self.domain_list.keys():      # no records in domain_list
            rp = RobotFileParser('http://%s/robots.txt' % hostname)
            print("%s: fetching %s" % (url, rp.url))
            try:
                rp.read()                                # get new robots.txt
            except IOError, e:                           # url's server not available(connection timeout)
                log.error(str(e))
                rp.disallow_all = True                   # reject all request
            self.domain_list[hostname] = rp              # add domain entry into domain_list
        else:
            rp = self.domain_list[hostname]              # get old robots.txt in domain_list
        return rp.can_fetch('*', url)

    def increase_running(self):
        self.lock.acquire()
        self.running += 1
        self.lock.release()

    def decrease_running(self):
        self.lock.acquire()
        self.running -= 1
        self.lock.release()


class Worker(Thread):
    """worker thread in spider to fetch webpage"""
    def __init__(self, spider):
        super(Worker, self).__init__()
        self.spider = spider
        self.status = True
        self.isDaemon = True
        self.start()

    def run(self):
        while self.status:
            try:
                url = self.spider.task_list.get(timeout = 1)
            except Empty:
                log.info('%s: task_list Empty' % self.name)
                continue
            self.spider.increase_running()
            if not self.spider.check_robots(url):
                log.info('%s - robots forbidden : %s' % (self.name, url))
                continue
            page = WebPage(url)
            print('%s prepare to fetch %s' % (self.name, url))
            if page.fetch():
                self.spider.db.save_data(page.get_data())
                for link in page.get_link():                        # retrive links from html
                    if link not in self.spider.visited_list:        # not visited yet
                        self.spider.extend_list.add(link)
            else:
                print('%s: Page fetch failed: %s' % (self.name, page.url))
            self.spider.decrease_running()

