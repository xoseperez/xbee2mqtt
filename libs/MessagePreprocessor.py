#! /usr/bin/python
# -*- utf-8 -*-
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

__app__ = "MQTT Message Preprocessor"
__version__ = '0.1'
__author__ = "Xose Perez"
__copyright__ = "Copyright (C) Xose Perez"
__license__ = 'TBD'

from Filters import FilterFactory

class MessagePreprocessor(object):

    default_topic_pattern = '/raw/{address}/{port}'
    publish_undefined_topics = True

    mapping = {}

    def load_map(self, map):
        for address, ports in map.iteritems():
            for port, value in ports.iteritems():
                config = {}
                if isinstance(value, dict):
                    config['topic'] = value.get('topic', self.default_topic_pattern.format(address=address, port=port))
                    config['filter'] = value.get('filter', None)
                    config['publish'] = value.get('publish', True)
                    config['timestampable'] = value.get('timestampable', False)
                else:
                    config['topic'] = value
                    config['filter'] = None
                    config['publish'] = True
                    config['timestampable'] = False
                self.mapping[address, port] = config

    def map(self, address, port, value):

        try:
            topic = self.mapping[(address, port)]['topic']
            publish = self.mapping[(address, port)]['publish']
            config = self.mapping[(address, port)]['filter']
            timestampable = self.mapping[(address, port)]['timestampable']
        except:
            topic = self.default_topic_pattern.format(address=address, port=port)
            publish = self.publish_undefined_topics
            config = None
            timestampable = False

        # Processing values
        if publish and config and config['type']:
            filter = FilterFactory(config['type'])
            if (filter):
                filter.configure(config.get('parameters', None))
                if filter.validate():
                    value = filter.process(value)

        return {
            'topic': topic,
            'value': value,
            'publish': publish,
            'timestampable': timestampable
        }

if __name__ == "__main__":
    processor = MessagePreprocessor();
    print processor.map('XXX', 3, 19)
    None
