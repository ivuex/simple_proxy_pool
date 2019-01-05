# -*- encoding:utf-8 -*-

import json
from flask import Flask, g, Response, make_response, jsonify
from .setting import DB_TYPE, DB_KEY
from simple_proxy_pool.db.rds import RedisClient
from simple_proxy_pool.db.ssdb import SsdbClient


__all__ = ['app']

app = Flask(__name__)


def get_conn():
    if not hasattr(g, 'conn'):
        if DB_TYPE == 'ssdb':
            g.conn = SsdbClient()
        else:
            g.conn = RedisClient()
    return g.conn

# def prepair_response(dict):
    # resp = make_response(jsonify(dict), 200)
    # resp.headers['Content-Type'] = 'application/json'
    # return Response(json.dumps(dict), content_type='application/json')
    # return resp



@app.route('/')
def index():
    return  '''<h2>Welcome to spiders.zhouyu.wiki\'s Proxy Pool System</h2><p>DB_TYPE: {}</p><p>: {}</p>
<p><a href='http://documents.zhouyu.wiki:3000/爬虫工程师简历.docx'>My Resume</a></p>
'''.format(DB_TYPE, DB_KEY)


@app.route('/random_best.json') # 附带分值
def random_best_json():
    """
    Get a proxy
    :return: json 附带分值
    """
    conn = get_conn()
    dict = conn.random_best_json()
    return Response(
        json.dumps(dict),
        content_type='application/json')


@app.route('/random_best')
def random_best():
    """
    Get a proxy
    :return: 随机代理
    """
    conn = get_conn()
    return conn.random_best()


@app.route('/count')
def get_count():
    """
    Get the count of proxies
    :return: 代理池总数
    """
    conn = get_conn()
    return str(conn.count())


@app.route('/count_lucky')
def get_count_lucky():
    """
    Get the count of proxies
    :return 代理池中能用（分数为6到10）但不稳定的代理
    """
    conn = get_conn()
    return str(conn.count_lucky())


@app.route('/count_vip')
def get_count_vip():
    """
    Get the count of proxies
    :return: 代理池质量较高（分数为6到10）的代理数量
    """
    conn = get_conn()
    return str(conn.count_vip())


@app.route('/all.json')
def all():
    """
    Get the count of proxies
    :return: json 代理池总量
    """
    conn = get_conn()
    return Response(
        json.dumps(conn.all()),
        content_type='application/json')


@app.route('/all_lucky.json')
def all_lucky():
    """
    Get the count of proxies
    :return: json 代理池中能用（分数为INITIAL_SCORE+1到MAX_SCORE）但不稳定的代理
    """
    conn = get_conn()
    return Response(
        json.dumps(conn.all_lucky()),
        content_type='application/json')


@app.route('/all_vip.json')
def all_vip():
    """
    Get the count of proxies
    :return: json 代理池中质量最高 (分数为MAX_SCORE) 的代理总数
    """
    conn = get_conn()
    return Response(
        json.dumps(conn.all_vip()),
        content_type='application/json')


if __name__ == '__main__':
    app.run()
