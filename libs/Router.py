#! /usr/bin/python
# -*- utf-8 -*-
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

class Router(object):

    default_topic_pattern = '/raw/{address}/{port}'
    publish_undefined_topics = True

    routes = {}

    def load(self, routes):
        for address, ports in routes.iteritems():
            for port, value in ports.iteritems():
                self.routes[address, port] = value

    def forward(self, address, port):
        try:
            topic = self.routes[(address, port)]
        except:
            if self.publish_undefined_topics:
                topic = self.default_topic_pattern.format(address=address, port=port)
            else:
                topic = False
        return topic
