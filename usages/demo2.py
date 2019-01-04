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

