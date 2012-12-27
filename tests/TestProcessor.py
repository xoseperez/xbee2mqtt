#! /usr/bin/python

import os,sys
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir)

import unittest

from libs.Processor import Processor

class TestProcessor(unittest.TestCase):

    def test_unknown(self):
        processor = Processor()
        processor.load({
            '/test/linear': { 'type': 'linear', 'parameters':{ 'slope': 2, 'offset': 1}},
        })
        self.assertEquals(21, processor.map('/test/linear', 10))
        self.assertEquals(0, processor.map('/test/linear/1', 0))
        self.assertEquals(10, processor.map('/test/linear/2', 10))

    def test_linear(self):
        processor = Processor()
        processor.load({
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
        processor = Processor()
        processor.load({
            '/test/enum': { 'type': 'enum', 'parameters':{ 0: 'off', 1: 'on'}},
        })
        self.assertEquals('on', processor.map('/test/enum', 1))
        self.assertEquals('off', processor.map('/test/enum', 0))
        self.assertEquals('on', processor.map('/test/enum', 3))

    def test_step(self):
        processor = Processor()
        processor.load({
            '/test/step': { 'type': 'step', 'parameters':{ 2: 1, 4: 2, 5: 3}},
        })
        self.assertEquals(1, processor.map('/test/step', 0))
        self.assertEquals(1, processor.map('/test/step', 2))
        self.assertEquals(2, processor.map('/test/step', 3))
        self.assertEquals(3, processor.map('/test/step', 10))

    def test_boolean(self):
        processor = Processor()
        processor.load({
            '/test/boolean': { 'type': 'boolean' },
        })
        self.assertEquals(0, processor.map('/test/boolean', 0))
        self.assertEquals(1, processor.map('/test/boolean', 1))
        self.assertEquals(1, processor.map('/test/boolean', -1))
        self.assertEquals(1, processor.map('/test/boolean', 5))

    def test_not(self):
        processor = Processor()
        processor.load({
            '/test/not': { 'type': 'not' },
        })
        self.assertEquals(1, processor.map('/test/not', 0))
        self.assertEquals(0, processor.map('/test/not', 1))
        self.assertEquals(0, processor.map('/test/not', -1))
        self.assertEquals(0, processor.map('/test/not', 5))

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestProcessor)
    unittest.TextTestRunner(verbosity=2).run(suite)
