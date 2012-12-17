#! /usr/bin/python
# -*- utf-8 -*-
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

__app__ = "MQTT Message Preprocessor"
__version__ = '0.1'
__author__ = "Xose Perez"
__copyright__ = "Copyright (C) Xose Perez"
__license__ = 'TBD'

class MessagePreprocessor(object):

    default_topic_pattern = '/raw/{address}/{port}'

    mapping = {}

    def load_map(self, map):
        for address, ports in map.iteritems():
            for port, value in ports.iteritems():
                try:
                    self.mapping[address, port] = value['topic']
                except:
                    self.mapping[address, port] = value

    def map(self, address, port, value):
        try:
            topic = self.mapping[(address, port)]
        except:
            topic = self.default_topic_pattern.format(address=address, port=port)
        return [topic, value]

if __name__ == "__main__":
    processor = MessagePreprocessor();
    print processor.map('XXX', 3, 19)
    None
