#! /usr/bin/python
# -*- coding: utf-8 -*-
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

#   Xbee to MQTT gateway
#   Copyright (C) 2012 by Xose Pérez
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

__author__ = "Xose Pérez"
__contact__ = "xose.perez@gmail.com"
__copyright__ = "Copyright (C) Xose Pérez"
__license__ = 'GPL v3'

from Filters import FilterFactory

class Processor(object):
    """
    Processes values using the appropriate filter strategy
    """

    _filters = {}

    def __init__(self, filters):
        """
        Constructor, loads the strategy mappings
        """
        self._filters = filters

    def process(self, topic, value):
        """
        Gets the filter strategy for the given topic,
        instantiates a filter for that strategy using the FilterFactory and
        requests the filter to process the input value
        """

        try:
            config = self._filters[topic]
            if not isinstance(config, list):
                config = [config]
            for element in config:
                filter = FilterFactory(element.get('type', None))
                if (filter):
                    filter.configure(element.get('parameters', None))
                    if filter.validate():
                        value = filter.process(value)

        except:
            pass

        return value
