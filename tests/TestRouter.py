#! /usr/bin/python
# -*- coding: utf-8 -*-

"""
TestRouter.py

Xose Pérez, 2012
xose.perez@gmail.com

Tests the Router
"""

import unittest

from libs.Router import Router

class TestRouter(unittest.TestCase):

    def test_known_routes(self):
        router = Router()
        router.publish_undefined_topics = False
        router.load({
            'aaa': { 'dio12': '/aaa/status'},
            'bbb': { 'adc7': '/bbb/battery'}
        })
        self.assertEquals('/aaa/status', router.forward('aaa', 'dio12'))
        self.assertFalse(router.forward('aaa', 'dio1'))
        self.assertFalse(router.forward('bbb', 'dio12'))
        self.assertEquals('/bbb/battery', router.forward('bbb', 'adc7'))

    def test_unknown_routes(self):
        router = Router()
        router.default_topic_pattern = '/raw/{address}/{port}'
        router.publish_undefined_topics = True
        router.load({
            'aaa': { 'dio12': '/aaa/status'},
        })
        self.assertEquals('/aaa/status', router.forward('aaa', 'dio12'))
        self.assertEquals('/raw/aaa/dio1', router.forward('aaa', 'dio1'))
        self.assertEquals('/raw/bbb/dio12', router.forward('bbb', 'dio12'))

if __name__ == '__main__':
    unittest.main()
