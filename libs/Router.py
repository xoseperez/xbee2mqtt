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

class Router(object):
    """
    Performs the mapping between radios addresses and port to MQTT topics
    """

    default_topic_pattern = '/raw/{address}/{port}'
    publish_undefined_topics = True

    routes = {}

    def load(self, routes):
        """
        Stores the routes
        """
        for address, ports in routes.iteritems():
            for port, value in ports.iteritems():
                self.routes[address, port] = value

    def forward(self, address, port):
        """
        Tries to match the radio [address,port] tuple to a defined route.
        If the is no defined route checks if it has to generate one using the default_topic_pattern value
        """
        try:
            topic = self.routes[(address, port)]
        except:
            if self.publish_undefined_topics:
                topic = self.default_topic_pattern.format(address=address, port=port)
            else:
                topic = False
        return topic
