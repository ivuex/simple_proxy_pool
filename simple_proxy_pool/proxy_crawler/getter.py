# -*- encoding:utf-8 -*-

from simple_proxy_pool.db.rds import RedisClient
from simple_proxy_pool.db.ssdb import SsdbClient
from simple_proxy_pool.proxy_crawler.crawler import Crawler
from simple_proxy_pool.setting import *
import sys

class Getter():
    def __init__(self):
        if DB_TYPE == 'ssdb':
            self.conn = SsdbClient()
        else:
            self.conn = RedisClient()
        # self.conn = RedisClient()
        self.crawler = Crawler()
    
    def is_over_threshold(self):
        """
        判断是否达到了代理池限制
        """
        if self.conn.count() >= POOL_UPPER_THRESHOLD:
            return True
        else:
            return False
    
    def run(self):
        print('获取器开始执行')
        if not self.is_over_threshold():
            for callback_label in range(self.crawler.__CrawlFuncCount__):
                callback = self.crawler.__CrawlFunc__[callback_label]
                # 获取代理
                proxies = self.crawler.get_proxies(callback)
                sys.stdout.flush()
                for proxy in proxies:
                    self.conn.add(proxy)
