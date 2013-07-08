#! /usr/bin/python
# -*- coding: utf-8 -*-

__author__ = "Xose Pérez"
__contact__ = "xose.perez@gmail.com"
__copyright__ = "Copyright (C) Xose Pérez"
__license__ = 'GPL v3'

import unittest

from libs.processor import Processor

class TestProcessor(unittest.TestCase):

    def test_chained(self):
        processor = Processor({
            '/test/chained': [
                { 'type': 'linear', 'parameters':{ 'slope': 0.5, 'offset': 1}},
                { 'type': 'round', 'parameters':{ 'decimals': 0}},
            ],
        })
        self.assertEquals(7, processor.process('/test/chained', '11'))

    def test_unknown(self):
        processor = Processor({
            '/test/linear': { 'type': 'linear', 'parameters':{ 'slope': 2, 'offset': 1}},
        })
        self.assertEquals(21, processor.process('/test/linear', '10'))
        self.assertEquals('0', processor.process('/test/linear/1', '0'))
        self.assertEquals('10', processor.process('/test/linear/2', '10'))

    def test_round(self):
        processor = Processor({
            '/test/round/1': { 'type': 'round', 'parameters':{ 'decimals': 2}},
        })
        self.assertEquals(997.54, processor.process('/test/round/1', '997.5412'))

    def test_linear(self):
        processor = Processor({
            '/test/linear/1': { 'type': 'linear', 'parameters':{ 'slope': 2, 'offset': 1}},
            '/test/linear/2': { 'type': 'linear', 'parameters':{ 'slope': 0, 'offset': 1}},
            '/test/linear/3': { 'type': 'linear', 'parameters':{ 'slope': -1, 'offset': 0}},
            '/test/linear/4': { 'type': 'linear', 'parameters':{ 'slope': .01, 'offset': 0}},
        })
        self.assertEquals(21, processor.process('/test/linear/1', '10'))
        self.assertEquals(1, processor.process('/test/linear/1', '0'))
        self.assertEquals(1, processor.process('/test/linear/2', '10'))
        self.assertEquals(1, processor.process('/test/linear/2', '4'))
        self.assertEquals(0, processor.process('/test/linear/3', '0'))
        self.assertEquals(-6, processor.process('/test/linear/3', '6'))
        self.assertEquals(997.5412, processor.process('/test/linear/4', '99754.12'))

    def test_enum(self):
        processor = Processor({
            '/test/enum': { 'type': 'enum', 'parameters':{ 0: 'off', 1: 'on'}},
        })
        self.assertEquals('on', processor.process('/test/enum', '1'))
        self.assertEquals('off', processor.process('/test/enum', '0'))
        self.assertEquals('on', processor.process('/test/enum', '3'))

    def test_step(self):
        processor = Processor({
            '/test/step': { 'type': 'step', 'parameters':{ 2: 1, 4: 2, 5: 3}},
        })
        self.assertEquals(1, processor.process('/test/step', '0'))
        self.assertEquals(1, processor.process('/test/step', '2'))
        self.assertEquals(2, processor.process('/test/step', '3'))
        self.assertEquals(3, processor.process('/test/step', '10'))

    def test_boolean(self):
        processor = Processor({
            '/test/boolean': { 'type': 'boolean' },
        })
        self.assertEquals(0, processor.process('/test/boolean', '0'))
        self.assertEquals(1, processor.process('/test/boolean', '1'))
        self.assertEquals(1, processor.process('/test/boolean', '-1'))
        self.assertEquals(1, processor.process('/test/boolean', '5'))

    def test_not(self):
        processor = Processor({
            '/test/not': { 'type': 'not' },
        })
        self.assertEquals(1, processor.process('/test/not', '0'))
        self.assertEquals(0, processor.process('/test/not', '1'))
        self.assertEquals(0, processor.process('/test/not', '-1'))
        self.assertEquals(0, processor.process('/test/not', '5'))

    def test_format(self):
        processor = Processor({
            '/test/format1': { 'type': 'format', 'parameters':{'format': 'Current power consumption: {value}W'} }
        })
        self.assertEquals("Current power consumption: 200W", processor.process('/test/format1', '200'))

    def test_regexp(self):
        processor = Processor({
            '/test/regexp1': { 'type': 'regexp', 'parameters':{'pattern': '(.*): (.*)', 'replacement': '\\1|\\2'} }
        })
        self.assertEquals("username|text", processor.process('/test/regexp1', 'username: text'))

if __name__ == '__main__':
    unittest.main()
