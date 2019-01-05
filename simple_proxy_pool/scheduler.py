# -*- encoding:utf-8 -*-

import time
from multiprocessing import Process
from simple_proxy_pool.app import app
from simple_proxy_pool.proxy_crawler.getter import Getter
from simple_proxy_pool.tester import Tester
from simple_proxy_pool.setting import *


class Scheduler():
    def schedule_tester(self, cycle=CHECK_DURATION_SECONDS):
        """
        定时测试代理
        """
        tester = Tester()
        while True:
            print('测试器开始运行')
            tester.run()
            time.sleep(cycle)
    
    def schedule_getter(self, cycle=FETCH_DURATION_SECONDS):
        """
        定时获取代理
        """
        getter = Getter()
        while True:
            print('开始抓取代理')
            getter.run()
            time.sleep(cycle)
    
    def schedule_api(self):
        """
        开启API
        """
        app.run(API_HOST, API_PORT)
    
    def run(self):
        print('代理池开始运行')
        
        tester_process = Process(target=self.schedule_tester)
        tester_process.start()
        
        getter_process = Process(target=self.schedule_getter)
        getter_process.start()
        
        api_process = Process(target=self.schedule_api)
        api_process.start()
