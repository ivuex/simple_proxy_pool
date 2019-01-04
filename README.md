## 项目
 + 

###### 关于http代理池
 + 在反反爬策略中，使用http代理(俗称换ip)是一个效果较好的方案
    * 代理的形式：ip:port
 + 以restful api的方式提供随机生成的可用代理是目前比较主流的方式
 + 获取途径有
    - 使用商业的代理池服务
        * 优点：稳定、海量ip、定期更新等
        * 成本：需要向服务提供商支付服务费    
    - 自建代理池服务
        * 优点：不用想服务提供商支付服务费
        * 成本：需要自己搭建及维护、需要主机运行等
    - 其他
        * 缺点：可靠性面临考验
###### 该项目是**自建代理池服务**, 实现的模块分为以下几部分
 +  获取 /simple_proxy_pool/simple_proxy_pool/proxy_crawler/*.py
    - 从商业代理商提供的免费代理列表里将代理提取出来
        * 付费代理和免费代理都可以
        * 从不同代理源获取可保证地区分布更散(使用时爬虫特征更不明显) 
        * 在同样可访问的前提下，品质由高到低排序为: 高匿代理、混淆代理、匿名代理、透明代理
 + 储存 /simple_proxy_pool/simple_proxy_pool/db/*.py
    - 要具备以下功能
        * 储存抓取到的代理
        * 要保证代理不重复
        * 要能动态处理(增删查改)每个代理
 + 检测 /simple_proxy_pool/simple_proxy_pool/tester.py
    - 要定时检测数据库中代理的有效性
        * 要设置一个检测链接，针对性要强就设置为数据目标网站，通用型要强可以设置为 https://www.baidu.com (因为稳定且响应体相对小)
        * 每个代理需要一个标示来标示(对于Redis有序集合就是score值)可用性
    - 检测规则    
        * 新获取的代理score设置为5 (因为自建代理大多数情况是从免费代理中爬取，代理不可用的可能性很高，所以检测5次够了)
        * 如果检测通过就设置为10, 代表完全可用
        * 每次检测不通过(可能原因有：不可用，暂时忙，其他原因造成的不稳定，等)时，就将代理的score减1
        * 分数越低为越不可用, 当分数等于0时就从数据库删除
 + 接口 /simple_proxy_pool/simple_proxy_pool/app.py
    - 使用flask实现一个Restful Api
    - 该Api要具备以下功能
        * 添加代理
        * 删除代理
        * 修改代理的score值
###### 环境搭建
 + 安装 Python >= 3.5
 + 安装 python 依赖模块
```
# 1.
mkvirtualenv simple_proxy_pool
# 2.
pip3 install aiohttp Flask redis requests
   # 或者
pip3 install -r requirements.txt   
```
 + 数据库        
    - 默认使用ssdb
        * 使用硬盘储存，基于leveldb，存取速度依然很快，号称redis（内存储存）的替代品
        * NoSql，不占用端口
        * 适合同一主机跑比较多的服务
    - 兼容了redis    
        * 因为redis群众基础好啊
    - 配置方式
        * 在/simple_proxy_pool/settings.py中修改 DB_TYPE ， 可选项为 'redis' 和 'ssdb'
```
# filename /simple_proxy_pool/settings.py
# DB_TYPE = 'redis'
DB_TYPE = 'ssdb'
```        
 + 运行
```
# 在项目根目录中
python3 work.py
``` 

 + api接口
    - /random_best 
        * 如果有**满分代理**就随机返回满分代理
        * 如果没有**满分代理**就返回可用但不稳定的代理
        * 不然就随机返回一个爬取到的尚未测试通过的代理
        * content-type: "text/plain"
        * 格式: ip:port
    - /random_best.json
        * 如果有**满分代理**就随机返回满分代理及分数
        * 如果没有**满分代理**就返回可用但不稳定的代理及分数
        * 不然就随机返回一个爬取到的尚未测试通过的代理及分数
        * content-type: "application/json"
        * 格式: {"ip:port": score} 
    - /count
        * 代理总数
        * content-type: "text/plain"
        * 格式: 数字
    - /count_lucky
        * 可用但是不稳定的代理数量
        * content-type: "text/plain"
        * 格式: 数字
    - /count_vip
        * 非常稳定的代理数量
        * content-type: "text/plain"
        * 格式: 数字
    - /all.json
        * 所有的代理及分数
        * content-type: "application/json"
        * 格式: {"ip_a:port_a": score_a, "ip_b:port_b": score_b, ...}
    - /all_lucky.json
        * 可用但是不稳定的代理及分数
        * content-type: "application/json"
        * 格式: {"ip_a:port_a": score_a, "ip_b:port_b": score_b, ...}
    - /all_vip.json
        * 非常稳定的代理及分数
        * content-type: "application/json"
        * 格式: {"ip_a:port_a": MAX_SCORE, "ip_b:port_b": MAX_SCORE, ...}
 + 可以在业务代码中根据代理的分数酌情优化相关逻辑       
 
###### 使用代理的demo 
```
# -*- coding:utf-8 -*-
# filename: /simple_proxy_pool/simple_proxy_pool/usages/demo2.py

import os
import sys
import requests

dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, dir)

PROXY_POOL_URL = 'http://127.0.0.1:5555/random_best'
'''
/simple_proxy_pool/simple_proxy_pool/setting里设置的跟这个一样会比较有有效
比如目标网站封IP封掉一些代理的情况
'''
TEST_URL = 'https://www.baidu.com'

def get_proxy():
    try:
        response = requests.get(PROXY_POOL_URL)
        if response.status_code == 200:
            return response.text
    except ConnectionError:
        return None


def crawl(url, proxy):
    proxies = {
        "http": "http://" + proxy,
        "https": "http://"+ proxy,
    }
    r = requests.get(url, proxies=proxies)
    return r.text


def main():
    html = crawl(TEST_URL, get_proxy())
    print(html)

if __name__ == '__main__':
    main()
```

# ENJOY IT
