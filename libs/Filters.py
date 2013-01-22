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

from datetime import datetime

class FilterFactory(object):
    """
    Filter factory, returns the appropriate filter given the type
    """

    filters = []

    @staticmethod
    def register(filter):
        """
        Registers a new filter class
        """
        FilterFactory.filters.append(filter)

    def __new__(self, type):
        """
        Constructor, returns an instance of a filter given type
        """
        for filter in self.filters:
            if filter.name == type:
                return filter()
        return None

class Filter(object):
    """
    Abstract class for a filter
    """

    name = ''

    parameters = None

    required = []

    def configure(self, parameters):
        """
        Loads the configuration parameters
        """
        self.parameters = parameters

    def validate(self):
        """
        Validates the configuration parameters
        """
        for key in self.required:
            if key not in self.parameters:
                return False
        return True

    def process(self, value):
        """
        Processes the value
        """
        return value

class LinearFilter(Filter):
    """
    Simple linear filter: y=ax+b
    """
    name = 'linear'
    required = ['slope', 'offset']
    def process(self, value):
        return int(self.parameters['slope'] * value + self.parameters['offset'])
FilterFactory.register(LinearFilter)

class BooleanFilter(Filter):
    """
    Boolean casting filter: y=bool(x)
    """
    name = 'boolean'
    required = []
    def process(self, value):
        return 0 if value == 0 else 1
FilterFactory.register(BooleanFilter)

class NotFilter(Filter):
    """
    Boolean NOT filter: y=!x
    """
    name = 'not'
    required = []
    def process(self, value):
        return 1 if value == 0 else 0
FilterFactory.register(NotFilter)

class EnumFilter(Filter):
    """
    Enumeration filter, returns the value for a dictionary which key matches the input value
    """
    name = 'enum'
    required = []
    def process(self, value):
        for from_value, to_value in self.parameters.iteritems():
            if value == from_value:
                return to_value
        return to_value
FilterFactory.register(EnumFilter)

class StepFilter(Filter):
    """
    Step filter
    """
    name = 'step'
    required = []
    def process(self, value):
        for threshold, to_value in self.parameters.iteritems():
            if value <= threshold:
                return to_value
        return to_value
FilterFactory.register(StepFilter)

class FormatFilter(Filter):
    """
    String format filter
    """
    name = 'format'
    required = ['format']
    def process(self, value):
        now = datetime.now()
        value = self.parameters['format'].format(
            value=value,
            date=now.strftime('%Y-%m-%d'),
            time=now.strftime('%H:%M:%S'),
            datetime=now.strftime('%Y-%m-%d %H:%M:%S')
        )
        return value
FilterFactory.register(FormatFilter)

