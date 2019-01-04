import redis
from simple_proxy_pool.setting import REDIS_HOST, REDIS_PORT, REDIS_PASSWORD
from simple_proxy_pool.setting import MAX_SCORE, MIN_SCORE, INITIAL_SCORE, DB_KEY
from random import choice, randint
import re


class RedisClient(object):

    def __init__(self, host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD):
        """
        初始化
        :param host: Redis 地址
        :param port: Redis 端口
        :param password: Redis密码
        """
        self.rds = redis.StrictRedis(host=host, port=port, password=password, decode_responses=True)
    
    def add(self, proxy, score=INITIAL_SCORE):
        """
        添加代理，设置分数为最高
        :param proxy: 代理
        :param score: 分数
        :return: 添加结果
        """
        if not re.match('\d+\.\d+\.\d+\.\d+\:\d+', proxy):
            print('代理不符合规范', proxy, '丢弃')
            return
        if not self.rds.zscore(DB_KEY, proxy):
            return self.rds.zadd(DB_KEY, score, proxy)

    def decrease(self, proxy):
        """
        代理值减一分，小于最小值则删除
        :param proxy: 代理
        :return: 修改后的代理分数
        """
        score = self.rds.zscore(DB_KEY, proxy)
        if score and score > MIN_SCORE:
            print('代理', proxy, '当前分数', score, '减1')
            return self.rds.zincrby(DB_KEY, proxy, -1)
        else:
            print('代理', proxy, '当前分数', score, '移除')
            return self.rds.zrem(DB_KEY, proxy)
    
    def exists(self, proxy):
        """
        判断是否存在
        :param proxy: 代理
        :return: 是否存在
        """
        return not self.rds.zscore(DB_KEY, proxy) == None
    
    def max(self, proxy):
        """
        将代理设置为MAX_SCORE
        :param proxy: 代理
        :return: 设置结果
        """
        print('代理', proxy, '可用，设置为', MAX_SCORE)
        return self.rds.zadd(DB_KEY, MAX_SCORE, proxy)

    def batch(self, start, stop):
        """
        批量获取
        :param start: 开始索引
        :param stop: 结束索引
        :return: 代理列表
        """
        return self.rds.zrevrange(DB_KEY, start, stop - 1)

    def count(self):
        """
        获取数量
        :return: json 代理池总量
        """
        return self.rds.zcount(DB_KEY, MIN_SCORE, MAX_SCORE)

    def count_lucky(self):
        """
        获取数量
        :returny json 代理池中能用（分数为INITIAL_SCORE+1到MAX_SCORE）但不稳定的代理
        """
        return self.rds.zcount(DB_KEY, INITIAL_SCORE + 1, MAX_SCORE)

    def count_vip(self):
        """
        获取数量
        :return: json 代理池中质量最高 (分数为MAX_SCORE) 的代理总数
        """
        return self.rds.zcount(DB_KEY, MAX_SCORE, MAX_SCORE)

    def to_proxies(self, mixed):
        # print(mixed)
        if isinstance(mixed, list):
            proxies = {}
            for pair in mixed:
                proxy, port = pair
                proxies[proxy] = port
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
        mixed = self.rds.zrangebyscore('universal_http_proxy', startscore, MAX_SCORE, withscores=True, score_cast_func=float)
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
            print(pair)
            return pair
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
        mixed = self.rds.zrangebyscore('universal_http_proxy', MIN_SCORE, MAX_SCORE, withscores=True, score_cast_func=float)
        proxies = self.to_proxies(mixed)
        return proxies

    def all_lucky(self):
        """
        获取高质量的代理（分数为6到10）
        :return 代理池中能用（分数为6到10）但不稳定的代理
        :return: 全部代理列表
        """
        mixed = self.rds.zrangebyscore('universal_http_proxy', MIN_SCORE+1, MAX_SCORE, withscores=True, score_cast_func=float)
        proxies = self.to_proxies(mixed)
        return proxies

    def all_vip(self):
        """
        获取高质量的代理（分数为10）
        :return: 全部代理列表
        """
        mixed = self.rds.zrangebyscore('universal_http_proxy', MAX_SCORE, MAX_SCORE, withscores=True, score_cast_func=float)
        proxies = self.to_proxies(mixed)
        return proxies


if __name__ == '__main__':
    conn = RedisClient()
    result = conn.all_vip()
    print(result)
