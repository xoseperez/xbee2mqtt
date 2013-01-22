#! /usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Xose Pérez"
__contact__ = "xose.perez@gmail.com"
__copyright__ = "Copyright (C) Xose Pérez"
__license__ = 'GPL v3'

import unittest

from libs.Processor import Processor

class TestProcessor(unittest.TestCase):

    def test_unknown(self):
        processor = Processor({
            '/test/linear': { 'type': 'linear', 'parameters':{ 'slope': 2, 'offset': 1}},
        })
        self.assertEquals(21, processor.map('/test/linear', 10))
        self.assertEquals(0, processor.map('/test/linear/1', 0))
        self.assertEquals(10, processor.map('/test/linear/2', 10))

    def test_linear(self):
        processor = Processor({
            '/test/linear/1': { 'type': 'linear', 'parameters':{ 'slope': 2, 'offset': 1}},
            '/test/linear/2': { 'type': 'linear', 'parameters':{ 'slope': 0, 'offset': 1}},
            '/test/linear/3': { 'type': 'linear', 'parameters':{ 'slope': -1, 'offset': 0}},
        })
        self.assertEquals(21, processor.map('/test/linear/1', 10))
        self.assertEquals(1, processor.map('/test/linear/1', 0))
        self.assertEquals(1, processor.map('/test/linear/2', 10))
        self.assertEquals(1, processor.map('/test/linear/2', 4))
        self.assertEquals(0, processor.map('/test/linear/3', 0))
        self.assertEquals(-6, processor.map('/test/linear/3', 6))

    def test_enum(self):
        processor = Processor({
            '/test/enum': { 'type': 'enum', 'parameters':{ 0: 'off', 1: 'on'}},
        })
        self.assertEquals('on', processor.map('/test/enum', 1))
        self.assertEquals('off', processor.map('/test/enum', 0))
        self.assertEquals('on', processor.map('/test/enum', 3))

    def test_step(self):
        processor = Processor({
            '/test/step': { 'type': 'step', 'parameters':{ 2: 1, 4: 2, 5: 3}},
        })
        self.assertEquals(1, processor.map('/test/step', 0))
        self.assertEquals(1, processor.map('/test/step', 2))
        self.assertEquals(2, processor.map('/test/step', 3))
        self.assertEquals(3, processor.map('/test/step', 10))

    def test_boolean(self):
        processor = Processor({
            '/test/boolean': { 'type': 'boolean' },
        })
        self.assertEquals(0, processor.map('/test/boolean', 0))
        self.assertEquals(1, processor.map('/test/boolean', 1))
        self.assertEquals(1, processor.map('/test/boolean', -1))
        self.assertEquals(1, processor.map('/test/boolean', 5))

    def test_not(self):
        processor = Processor({
            '/test/not': { 'type': 'not' },
        })
        self.assertEquals(1, processor.map('/test/not', 0))
        self.assertEquals(0, processor.map('/test/not', 1))
        self.assertEquals(0, processor.map('/test/not', -1))
        self.assertEquals(0, processor.map('/test/not', 5))

    def test_format(self):
        processor = Processor({
            '/test/format1': { 'type': 'format', 'parameters':{'format': 'Current power consumption: {value}W'} }
        })
        self.assertEquals("Current power consumption: 200W", processor.map('/test/format1', 200))

if __name__ == '__main__':
    unittest.main()
