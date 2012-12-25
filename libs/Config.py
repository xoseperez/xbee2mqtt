#! /usr/bin/python
# -*- utf-8 -*-
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

import yaml

class Config(object):

    config = None

    def __init__(self, filename):
        handler = file(filename, 'r')
        self.config = yaml.load(handler)
        handler.close()

    def get(self, section, key, default=None):
        response = default
        if self.config.has_key(section):
            if self.config[section].has_key(key):
                response = self.config[section][key]
        return response

