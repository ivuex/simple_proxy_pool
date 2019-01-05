# -*- encoding:utf-8 -*-

import re
from random import choice, randint
from simple_proxy_pool.setting import MAX_SCORE, MIN_SCORE, INITIAL_SCORE, DB_KEY, POOL_UPPER_THRESHOLD


class SsdbClient(object):

    def __init__(self):
        import pyssdb
        self.c = pyssdb.Client(host='127.0.0.1', port=4478)
        self.proxy_reg = re.compile(r'\d+\.\d+\.\d+\.\d+')

    def add(self, proxy, score=INITIAL_SCORE):
        """
        添加代理，设置分数为最高
        :param proxy: 代理
        :param score: 分数
        :return: 添加结果
        """
        if not re.match(self.proxy_reg, proxy):
            print('代理不合规范', proxy, '丢弃')
            return
        if not self.c.zget(DB_KEY, proxy):
            return self.c.zset(DB_KEY, proxy, INITIAL_SCORE)

    def decrease(self, proxy):
        """
        代理值减一分，小于最小值则删除
        :param proxy: 代理
        :return: 修改后的代理分数
        """
        score = self.c.zget(DB_KEY, proxy)
        if type(score) == int  and score > MIN_SCORE:
            print('代理', proxy, '当前分数', score, '减1')
            return self.c.zincr(DB_KEY, proxy, -1)
        else:
            print('代理', proxy, '当前分数', score, '移除')
            return self.c.multi_zdel(DB_KEY, proxy)

    def exists(self, proxy):
        """
        判断是否存在
        :param proxy: 代理
        :return: 是否存在
        """
        return bool(self.c.zexists(DB_KEY, proxy))

    def max(self, proxy):
        """
        将代理设置为MAX_SCORE
        :param proxy: 代理
        :return: 设置结果
        """
        if self.c.zset(DB_KEY, proxy,  MAX_SCORE,):
            print('代理', proxy, '可用，设置为', MAX_SCORE)

    def batch(self, start, stop):
        """
        批量获取
        :param start: 开始索引
        :param stop: 结束索引
        :return: 代理列表
        """
        limit = stop - start + 1
        return self.c.zkeys(DB_KEY, start, MIN_SCORE, MAX_SCORE, limit)

    def count(self):
        """
        获取数量
        :return: json 代理池总量
        """
        return int(self.c.zcount(DB_KEY, MIN_SCORE, MAX_SCORE))

    def count_lucky(self):
       """
       获取数量
       :return json 代理池中能用（分数为INITIAL_SCORE+1到MAX_SCORE）但不稳定的代理
       """
       return int(self.c.zcount(DB_KEY, INITIAL_SCORE+1, MAX_SCORE))

    def count_vip(self):
        """
        获取数量
        :return: json 代理池中质量最高 (分数为MAX_SCORE) 的代理总数
        """
        return int(self.c.zcount(DB_KEY, MAX_SCORE, MAX_SCORE))

    def to_proxies(self, mixed):
        # print(mixed)
        if isinstance(mixed, list):
            proxies = {}
            while len(mixed) >= 2:
                proxy = str(mixed.pop(-2), 'utf-8')
                port = int(mixed.pop(-1))
                proxies[proxy] = port
            print(proxies, '107-107')
            return proxies
        else:
            print('arguments mixed must be list, but {} got: '.format(type(mixed)), mixed)
            raise Exception

    def get_random_pair_by_startscore(self, startscore):
        # total = self.c.zcount(DB_KEY)
        '''
        :return 随机返回分值大于 startscore的键值数组 pair
            pair[0] 为 代理
            pair[1] 为 分值
        '''
        # mixed = self.rds.zrangebyscore('universal_http_proxy', startscore, MAX_SCORE, withscores=True, score_cast_func=float)
        mixed = self.c.zscan('universal_http_proxy', '', startscore, MAX_SCORE, POOL_UPPER_THRESHOLD)
        proxies = self.to_proxies(mixed)
        if not proxies:
            print('没有获取到代理')
            raise Exception
        proxy = choice(list(proxies.keys()))
        pair = {proxy: proxies[proxy]}
        return pair

    def get_best_random_pair(self):
        """
        随机获取有效代理，首先尝试获取最满分数代理
        如果不存在，获取分数为INITIAL_SCORE到MAX_SCORE之间的代理
        如果还是不存在，就随机获取
        否则异常
        :return 随机返回分值大于 startscore的键值数组 pair
            pair[0] 为 代理
            pair[1] 为 分值
        """
        pair = self.get_random_pair_by_startscore(MAX_SCORE)
        if not pair:
            pair = self.get_random_pair_by_startscore(INITIAL_SCORE)
            if not pair:
                pair = self.get_random_pair_by_startscore(MIN_SCORE)
        return pair

    def random_best_json(self):
        pair = self.get_best_random_pair()
        if pair:
            print(str(pair))
            return str(pair)
        else:
            print('没有获取到pair')

    def random_best(self):
        """
        随机获取有效代理，首先尝试获取最高分数代理，如果不存在，按照排名获取，否则异常
        :return: 随机代理
        """
        pair = self.get_best_random_pair()
        if pair:
            proxy = list(pair.keys())[0]
            print(proxy)
            return proxy
        else:
            print('没有获取到pair.')
            return ''

    def all(self):
        """
        获取全部代理
        :return: 全部代理列表
        """
        mixed = self.c.zscan(DB_KEY, '', MIN_SCORE, MAX_SCORE, POOL_UPPER_THRESHOLD)
        proxies = self.to_proxies(mixed)
        return proxies

    def all_lucky(self):
        """
        获取高质量的代理（分数为6到10）
        :return 代理池中能用（分数为6到10）但不稳定的代理
        :return: 全部代理列表
        """
        mixed = self.c.zscan(DB_KEY, '', INITIAL_SCORE+1, MAX_SCORE, POOL_UPPER_THRESHOLD)
        proxies = self.to_proxies(mixed)
        return proxies

    def all_vip(self):
        """
        获取高质量的代理（分数为10）
        :return: 全部代理列表
        """
        mixed = self.c.zscan(DB_KEY, '', MAX_SCORE, MAX_SCORE, POOL_UPPER_THRESHOLD)
        proxies = self.to_proxies(mixed)
        return proxies


if __name__ == '__main__':
    conn = SsdbClient()
    result = conn.all_vip()



