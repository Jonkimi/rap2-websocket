#!/usr/bin/python2
# -*- coding:utf-8 -*-

# Copyright 2019 Jonkimi
# All rights reserved.
# license that can be found in the LICENSE file.

from __future__ import print_function
# from builtins import input
from sys import stdout
import json
import os.path
import urllib2
import urlparse
import shutil
import argparse
import shlex
import ConfigParser

# test cookie 'koa.sid=7QC71YKGHTaOZUbeMHirZjicr0MN8-fX; koa.sid.sig=h0Q0zcHLVyJ_qQVxfwD_9pvXSLE'
server = 'http://127.0.0.1:8088'
repo_url = '{0}/repository/get?id={1}'
mock_url_prefix = '{0}/app/mock/{1}/'
#脚本所在目录
mock_dir = os.path.split(os.path.realpath(__file__))[0]
example_script = u'test'
example_json = u'test.json'


def send_req(url, cookie):
    '''
    向 rap2-delos 发送请求
    :param url:
    :param cookie:
    :return:
    '''
    print('send request: ', url)
    req = urllib2.Request(url)
    req.add_header('cookie', cookie)
    try:
        response = urllib2.urlopen(req, timeout=60)
    except urllib2.HTTPError as err:
        print("HTTP error({0}): {1}".format(err.errno, err.strerror))
        response_str = None
    except IOError as err:
        print("IO error({0}): {1}, please check your repo id and cookie.".format(err.errno, err.strerror))
        response_str = None
    else:
        response_str = response.read()
    return response_str


def mock_repo(repo_id, cookie):
    repo_str = send_req(repo_url.format(server, repo_id),cookie)
    if repo_str is None:
        return
    parsed_json = json.loads(repo_str)
    data = parsed_json['data']
    if data is not None:
        interfaces = [y for x in data['modules'] for y in x['interfaces']]
        # print json.dumps(interfaces)
        ws_interfaces = filter(lambda i: i['name'].startswith('ws'), interfaces)
        # print json.dumps(ws_interfaces)
        for ws in ws_interfaces:
            print('----------------------------------------')
            ws_url = ws['url']
            if ws_url.endswith('/'):
                ws_url = ws_url[:len(ws_url) - 1]
            name = os.path.basename(ws_url)
            if ws_url.startswith('/'):
                ws_url = ws_url[1: len(ws_url)]
            path = os.path.dirname(os.path.join(mock_dir, ws_url))
            print('path:', ws_url)

            # 创建目录
            try:
                if not os.path.exists(path):
                    os.makedirs(path)
            except OSError as err:
                print("OSError ({0}): {1}".format(err.errno, err.strerror))
            else:
                # 复制脚本
                shutil.copy(os.path.join(mock_dir, example_script), os.path.join(path, name))
                # 写入脚本配置
                with open(os.path.join(path, name + '.conf'), 'w') as mock_url:
                    mock_url.write(urlparse.urljoin(mock_url_prefix.format(server, repo_id), ws_url))
                print('mock {0} OK '.format(ws_url))


class MyArgumentParser(argparse.ArgumentParser):
    # =====================================
    # Command line argument parsing methods
    # =====================================
    def parse_args(self, args=None, namespace=None):
        args, argv = self.parse_known_args(args, namespace)
        if argv:
            raise ValueError('unrecognized arguments: %s' % ''.join(argv))
        return args


def handle():
    while True:
        stdout.flush()
        command = raw_input()
        if command is None or not command.startswith('mock '):
            print(APP_DESC)
        else:
            try:
                args = parser.parse_args(shlex.split(command[5:]))
            except ValueError as e:
                print(e.message)
            else:
                #print(args)
                if args.cookie is None or args.repo_id is None:
                    print(APP_DESC)
                else:
                    mock_repo(args.repo_id, args.cookie)


import sys

if __name__ == '__main__':

    sys.argv
    # def print_message():
    #     print("hh")
    APP_DESC = """usage: mock [-h] [-i repo-id] [-c cookie]

optional arguments:
  -h, --help       show this help message and exit
  -i, --repo-id    set repository id
  -c, --cookie     set auth cookie
"""

    parser = MyArgumentParser()
    parser.add_argument('-i', '--repo-id', type=int, help="")
    parser.add_argument('-c', '--cookie', type=str, help="")

    # 读取服务器配置
    config_path = os.path.join(mock_dir, "mock.conf")

    if not os.path.exists(config_path):
        print("config file mock.conf not exists.")
    else:
        cf = ConfigParser.ConfigParser()
        cf.read(config_path)
        server = cf.get('main', 'server')
        print(APP_DESC)
        handle()
