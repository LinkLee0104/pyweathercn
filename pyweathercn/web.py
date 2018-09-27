#!/usr/bin/python
# coding:utf-8

# pyweathercn - web.py
# 2018/5/22 16:32
# For running up tornado

__author__ = 'Benny <benny@bennythink.com>'

import json
import socket
from platform import uname

from concurrent.futures import ThreadPoolExecutor
from tornado import web, ioloop, httpserver, gen
from tornado.concurrent import run_on_executor
from pyweathercn.craw import make_json
from pyweathercn.utils import api
from pyweathercn.constant import CODE, BANNER


class BaseHandler(web.RequestHandler):
    def data_received(self, chunk):
        pass


class IndexHandler(BaseHandler):

    def get(self):
        help_msg = '''Welcome to pyweathercn!
        There are two ways to interact with this RESTAPI.
        The key parameter is city, and an optional parameter day.<br>
        The first one is GET method, invoke:
        <code>127.0.0.1:8888/weather?city=上海</code> - get full details
        <code>127.0.0.1:8888/weather?city=上海&day=2</code> - get 2 days details
        The second one is POST method, invoke <code>127.0.0.1:8888/weather</code>
         with url-encoded form as above. Post JSON is also supported.
        '''
        base = '''<!DOCTYPE html><html><head><title>Welcome to pyweathercn!</title></head>
        <body>%s</body></html>'''
        self.write(base % ('<pre>' + BANNER + '</pre>' + '<br>' + help_msg).replace('\n', '<br>'))

    def post(self):
        self.get()


class WeatherHandler(BaseHandler):
    executor = ThreadPoolExecutor(max_workers=20)

    @run_on_executor
    def run_request(self):
        """
        sign and return
        :return: hex and raw request in XML
        """
        # get parameter, compatibility with json
        if self.request.headers.get('Content-Type') == 'application/json':
            data = json.loads(self.request.body)
            city = data.get('city')
            day = data.get('day')
        else:
            city = self.get_argument('city', None)
            day = self.get_argument('day', None)
        # mandatory param missing
        if city is None:
            return make_json(4)
        # day, return specified day.
        elif day:
            data = make_json(city)
            try:
                sp = data['data']['forecast'][int(day)]
            except IndexError:
                sp = {"status": "error", "message": CODE.get(5)}
            return json.dumps(sp)
        # return whole json.
        else:
            return json.dumps(make_json(city))

    @api
    @gen.coroutine
    def get(self):
        self.set_header("Content-Type", "application/json")
        res = yield self.run_request()
        self.write(res)

    @api
    @gen.coroutine
    def post(self):
        self.set_header("Content-Type", "application/json")
        res = yield self.run_request()
        self.write(res)


def get_host_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 80))
    ip = s.getsockname()[0]
    s.close()
    return ip


class RunServer:
    handlers = [(r'/weather', WeatherHandler), (r'/', IndexHandler)]
    application = web.Application(handlers)

    @staticmethod
    def run_server(port=8888, host='0.0.0.0', **kwargs):
        tornado_server = httpserver.HTTPServer(RunServer.application, **kwargs)
        tornado_server.bind(port, host)

        if uname()[0] == 'Windows':
            tornado_server.start()
        else:
            tornado_server.start(None)

        try:
            print(BANNER)
            print('Server is running on http://%s:%s' % (get_host_ip(), port))
            ioloop.IOLoop.instance().current().start()
        except KeyboardInterrupt:
            ioloop.IOLoop.instance().stop()
            print('"Ctrl+C" received, exiting.\n')


if __name__ == "__main__":
    # import pyweathercn.utils
    # pyweathercn.utils.DB = r'C:\Users\Benny\PycharmProjects\pyweathercn\sample.sqlite'
    RunServer.run_server()