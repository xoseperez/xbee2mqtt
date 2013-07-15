#! /usr/bin/python
# -*- coding: utf-8 -*-
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

#   Xbee to MQTT gateway
#   Copyright (C) 2012-2013 by Xose Pérez
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
__copyright__ = "Copyright (C) 2012-2013 Xose Pérez"
__license__ = 'GPL v3'

import time
import logging

#from tests.SerialMock import Serial
from serial import Serial
from libs.config import Config
from libs.xbee_wrapper import XBeeWrapper

class Xbee2Console(object):

    xbee = None

    def log(self, level, message):
        if self.logger:
            self.logger.log(level, message)

    def xbee_on_message(self, address, port, value):
        """
        Message from the radio coordinator
        """
        self.log(logging.DEBUG, "%s %s %s" % (address, port, value))

    def run(self):
        """
        Entry point, initiates components and loops forever...
        """
        self.xbee.on_message = self.xbee_on_message
        self.xbee.log = self.log
        self.xbee.connect()

        try:
            while True:
                time.sleep(.1)
        except KeyboardInterrupt:
            pass

        self.xbee.disconnect()
        self.log(logging.INFO, "Exiting")

if __name__ == "__main__":

    config = Config('config/xbee2mqtt.yaml')

    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)

    serial = Serial(
        config.get('radio', 'port', '/dev/ttyUSB0'),
        config.get('radio', 'baudrate', 9600)
    )

    # Sample data when using SerialMock
    # serial.feed('920013a200406bfd090123010110008010000B00')  # IO Sample DIO12:1, ADC7(Supply Voltage):2816

    xbee = XBeeWrapper()
    xbee.serial = serial
    xbee.default_port_name = config.get('radio', 'default_port_name', 'serial')

    manager = Xbee2Console()
    manager.xbee = xbee
    manager.logger = logger
    manager.run()

