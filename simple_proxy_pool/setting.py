# -*- coding:utf-8 -*-

# Redis数据库地址
REDIS_HOST = '127.0.0.1'
# Redis端口
REDIS_PORT = 6379

# DB_TYPE = 'redis'
DB_TYPE = 'ssdb'

# Redis密码，如无填None
REDIS_PASSWORD = None

# 代理分数
MAX_SCORE = 50
MIN_SCORE = 0
INITIAL_SCORE = 5

VALID_STATUS_CODES = [200, 302]

# 代理池数量界限
POOL_UPPER_THRESHOLD = 99999999

# 检查周期
CHECK_DURATION_SECONDS = 20
# 获取周期
FETCH_DURATION_SECONDS = 300

'''
测试API
针对性要强就设置为数据目标网站
通用型要强可以设置为 https://www.baidu.com (因为稳定且响应体相对小)
'''

DB_KEY = 'universal_http_proxy'
TEST_URL = 'https://www.baidu.com'

# API配置
API_HOST = '0.0.0.0'
API_PORT = 5555

# 最大批测试量
BATCH_TEST_SIZE = 10
