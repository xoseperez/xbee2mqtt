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

import binascii

class Serial(object):
    """
    Serial Mock class, exposes the same API as the python-serial module
    """

    stream = ''
    length = 0
    index = 0

    data = ''

    def _split_len(self, seq, length):
        """
        Splits a string into length chunks
        """
        return [seq[i:i+length] for i in range(0, len(seq), length)]

    def __init__(self, port, baudrate):
        """
        Constructor, exposes same arguments but discards them
        """
        pass

    def feed(self, message):
        """
        Loads new messages to feed to the consumer
        """
        bytes = self._split_len(message,2)
        checksum = 0xFF - (sum([int(x,16) for x in bytes]) & 0xFF)
        message = '7e' + "%04x" % len(bytes) + message + "%02x" % checksum
        message = binascii.unhexlify(message)
        self.stream += message
        self.length = len(self.stream)

    def inWaiting(self):
        """
        Report the number of bytes pending to read
        """
        return self.length - self.index

    def read(self):
        """
        Feeds incoming bytes to the consumer
        """
        response = None
        if self.inWaiting() > 0:
            response = self.stream[self.index]
            self.index += 1
        return response

    def write(self, message):
        """
        Stores outgoing messages
        """
        self.data += message

    def close(self):
        """
        Does nothing :)
        """
        None
