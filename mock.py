#!/usr/bin/python2
# -*- coding:utf-8 -*-
from __future__ import print_function
#from builtins import input
from sys import stdout
import json
import os.path
import urllib2
import urlparse
import shutil
import argparse
import shlex

cookie = 'koa.sid=7QC71YKGHTaOZUbeMHirZjicr0MN8-fX; koa.sid.sig=h0Q0zcHLVyJ_qQVxfwD_9pvXSLE'
server = 'https://rap2-delos.example.com'
repo_url = '{0}/repository/get?id={1}'
mock_url_prefix = '{0}/app/mock/{1}/'

mock_dir = u'/root/ws'
example_script = u'test/test'
example_json = u'test/test.json'


def send_req(url):
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


def mock_repo(repo_id):
    repo_str = send_req(repo_url.format(server, repo_id))
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

            # 获取mock数据
            mock_data = send_req(urlparse.urljoin(mock_url_prefix.format(server, repo_id), ws_url))

            # 打印mock 数据
            mock_data = mock_data.replace('\r\n', ' ').replace('\n', ' ')
            print(mock_data)
            if mock_data is not None:
                # 创建目录
                try:
                    if not os.path.exists(path):
                        os.makedirs(path)
                except OSError as err:
                    print("OSError ({0}): {1}".format(err.errno, err.strerror))
                else:
                    # 复制脚本
                    shutil.copy(os.path.join(mock_dir,example_script), os.path.join(path, name))

                    # 写mock数据
                    with open(os.path.join(path, name + '.json'), 'w') as mock_json:
                        mock_json.write(mock_data)

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
                print(args)
                if args.cookie is not None:
                    cookie = args.cookie
                mock_repo(args.repo_id)
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
    confi_path = os.path.join(os.path.split(os.path.realpath(__file__))[0], "config.json")

    if not os.path.exists(confi_path):
        print("config file not exists.")
    else:
        with open(confi_path, 'r') as f:
            content = f.read()
            print("config: \n", content)
            config = json.loads(content)
            server = config['server']
            mock_dir = config['dir']
            print(APP_DESC)
            handle()
