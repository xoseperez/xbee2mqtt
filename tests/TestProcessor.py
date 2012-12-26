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
            '/xbee/linear': { 'type': 'linear', 'parameters':{ 'slope': 2, 'offset': 1}},
        })
        self.assertEquals(21, processor.map('/xbee/linear', 10))
        self.assertEquals(0, processor.map('/xbee/linear/1', 0))
        self.assertEquals(10, processor.map('/xbee/linear/2', 10))

    def test_linear(self):
        processor = Processor()
        processor.load({
            '/xbee/linear/1': { 'type': 'linear', 'parameters':{ 'slope': 2, 'offset': 1}},
            '/xbee/linear/2': { 'type': 'linear', 'parameters':{ 'slope': 0, 'offset': 1}},
            '/xbee/linear/3': { 'type': 'linear', 'parameters':{ 'slope': -1, 'offset': 0}},
        })
        self.assertEquals(21, processor.map('/xbee/linear/1', 10))
        self.assertEquals(1, processor.map('/xbee/linear/1', 0))
        self.assertEquals(1, processor.map('/xbee/linear/2', 10))
        self.assertEquals(1, processor.map('/xbee/linear/2', 4))
        self.assertEquals(0, processor.map('/xbee/linear/3', 0))
        self.assertEquals(-6, processor.map('/xbee/linear/3', 6))

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TestProcessor)
    unittest.TextTestRunner(verbosity=2).run(suite)
