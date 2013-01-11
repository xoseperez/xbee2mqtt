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

from xbee import XBee as _XBee

class XBee(object):
    """
    Helper class for the python-xbee module.
    It processes API packets into simple address/port/value groups.
    See http://code.google.com/r/xoseperez-python-xbee/
    """

    default_port_name = 'serial'

    serial = None
    xbee = None

    buffer = dict()

    def log(self, message):
        """
        Hook to log messages
        """
        pass

    def disconnect(self):
        """
        Closes serial port
        """
        self.xbee.halt()
        self.serial.close()
        return True

    def connect(self):
        """
        Creates an Xbee instance
        """
        try:
            self.xbee = _XBee(self.serial, callback=self.process)
        except:
            return False
        return True

    def process(self, packet):
        """
        Processes an incoming packet, supported packet frame ids:
            0x90: Zigbee Receive Packet
            0x92: ZigBee IO Data Sample Rx Indicator
        """

        self.log(packet)

        address = packet['source_addr_long']
        frame_id = int(packet['frame_id'])

        # Data sent through the serial connection of the remote radio
        if (frame_id == 90):

            # Some streams arrive split in different packets
            # we buffer the data until we get an EOL
            self.buffer[address] = self.buffer.get(address,'') + packet['data']
            count = self.buffer[address].count('\n')
            if (count):
                lines = self.buffer[address].splitlines()
                try:
                    self.buffer[address] = lines[count:][0]
                except:
                    self.buffer[address] = ''
                for line in lines[:count]:
                    line = line.rstrip()
                    try:
                        port, value = line.split(':', 1)
                    except:
                        value = line
                        port = self.default_port_name
                    self.on_message(address, port, value)

        # Data received from an IO data sample
        if (frame_id == 92):
            for port, value in packet['samples'].iteritems():
                if port[:3] == 'dio':
                    value = 1 if value else 0
                self.on_message(address, port, value)

    def on_message(self, address, port, value):
        """
        Hook for outgoing messages.
        For future use with Xbee attached actuators.
        """
        None

