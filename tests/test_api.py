#!/usr/bin/python
# coding:utf-8

# pyweathercn - test_api.py
# 2018/5/23 16:54
#

__author__ = 'Benny <benny@bennythink.com>'

import json
import sys
import unittest

from tornado.testing import AsyncHTTPTestCase
from tornado.escape import url_escape

sys.path.append('.')
from tests.deco import logger
from pyweathercn.web import RunServer


class TestAPI(AsyncHTTPTestCase):
    def get_app(self):
        return RunServer.application

    @logger
    def test_get(self):
        case = ['/weather?city=%s' % url_escape('呗'), '/weather?c=%s' % url_escape('北京'),
                '/weather?city=%s' % url_escape('北京'), '/weather?city=%s&day=2' % url_escape('北京')]
        result = [{'code': 400001, 'message': 'city not found.', 'error': 'city not found.'},
                  {'code': 400002, 'message': 'city param error', 'error': 'city param error'}
                  ]

        code = json.loads(self.fetch(case[0]).body.decode('utf-8'))
        assert result[0] == code

        code = json.loads(self.fetch(case[1]).body.decode('utf-8'))
        assert result[1] == code

        code = json.loads(self.fetch(case[2]).body.decode('utf-8'))
        assert code['city'] == '北京' and len(code['forecast']) != 0

        code = json.loads(self.fetch(case[3]).body.decode('utf-8'))
        assert '后天' in code['date']

    @logger
    def test_post(self):
        case = ['city=%s' % url_escape('无'), 'c=%s' % url_escape('北京'),
                'city=%s' % url_escape('北京'), 'city=%s&day=2' % url_escape('北京')]
        result = [{'code': 400001, 'message': 'city not found.', 'error': 'city not found.'},
                  {'code': 400002, 'message': 'city param error', 'error': 'city param error'}
                  ]

        code = json.loads(self.fetch('/weather', method='POST', body=case[0]).body.decode('utf-8'))
        assert result[0] == code

        code = json.loads(self.fetch('/weather', method='POST', body=case[1]).body.decode('utf-8'))
        assert result[1] == code

        code = json.loads(self.fetch('/weather', method='POST', body=case[2]).body.decode('utf-8'))
        assert code['city'] == '北京' and code.get('code') is None

        code = json.loads(self.fetch('/weather', method='POST', body=case[3]).body.decode('utf-8'))
        assert '后天' in code['date']


if __name__ == '__main__':
    unittest.main()
