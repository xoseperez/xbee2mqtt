#! /usr/bin/python
# -*- utf-8 -*-
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

from Filters import FilterFactory

class Processor(object):

    filters = {}

    def load(self, filters):
        for topic, filter in filters.iteritems():
            self.filters[topic] = filter

    def map(self, topic, value):

        try:
            config = self.filters[topic]
            filter = FilterFactory(config['type'])
            if (filter):
                filter.configure(config.get('parameters', None))
                if filter.validate():
                    value = filter.process(value)

        except:
            pass

        return value
