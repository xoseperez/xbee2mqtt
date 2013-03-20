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

import re
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
        return self.parameters['slope'] * float(value) + self.parameters['offset']
FilterFactory.register(LinearFilter)

class RoundFilter(Filter):
    """
    Rounds the number: y=round(x)
    """
    name = 'round'
    required = ['decimals']
    def process(self, value):
        value = round(float(value), self.parameters['decimals'])
        if self.parameters['decimals'] == 0:
            value = int(value)
        return value
FilterFactory.register(RoundFilter)

class BooleanFilter(Filter):
    """
    Boolean casting filter: y=bool(x)
    """
    name = 'boolean'
    required = []
    def process(self, value):
        return 0 if int(value) == 0 else 1
FilterFactory.register(BooleanFilter)

class NotFilter(Filter):
    """
    Boolean NOT filter: y=!x
    """
    name = 'not'
    required = []
    def process(self, value):
        return 1 if int(value) == 0 else 0
FilterFactory.register(NotFilter)

class EnumFilter(Filter):
    """
    Enumeration filter, returns the value for a dictionary which key matches the input value
    """
    name = 'enum'
    required = []
    def process(self, value):
        for from_value, to_value in self.parameters.iteritems():
            if str(value) == str(from_value):
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
            if float(value) <= threshold:
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

class RegExpFilter(Filter):
    """
    Regexp replace filter
    """
    name = 'regexp'
    required = ['pattern', 'replacement']
    def process(self, value):
        pattern = re.compile(self.parameters['pattern'])
        return pattern.sub(self.parameters['replacement'], value)
FilterFactory.register(RegExpFilter)

