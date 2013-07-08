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

import sys
import time
import signal
from datetime import datetime

from tests.SerialMock import Serial
#from serial import Serial
from libs.config import Config
from libs.xbee_wrapper import XBeeWrapper

class Xbee2Console(object):

    xbee = None

    def log(self, message):
        """
        Log method.
        TODO: replace with standard python logging facility
        """
        timestamp = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')
        sys.stdout.write("[%s] %s\n" % (timestamp, message))
        sys.stdout.flush()

    def cleanup(self, signal, frame):
        """
        Clean up connections and unbind ports
        """
        self.xbee.disconnect()
        self.log("[INFO] Exiting")
        sys.exit()

    def xbee_on_message(self, address, port, value):
        """
        Message from the radio coordinator
        """
        self.log("[DEBUG] %s %s %s" % (address, port, value))

    def xbee_connect(self):
        """
        Initiate connection to the radio coordinator via serial port
        """
        self.log("[INFO] Connecting to Xbee")
        if not xbee.connect():
            sys.exit()

    def run(self):
        """
        Entry point, initiates components and loops forever...
        """
        self.xbee.on_message = self.xbee_on_message
        self.xbee.log = self.log
        self.xbee_connect()

        signal.signal(signal.SIGINT, self.cleanup)

        while True:
            time.sleep(.01)

if __name__ == "__main__":

    config = Config('config/xbee2mqtt.yaml')

    manager = Xbee2Console()

    serial = Serial(
        config.get('radio', 'port', '/dev/ttyUSB0'),
        config.get('radio', 'baudrate', 9600)
    )

    xbee = XBeeWrapper()
    xbee.serial = serial
    xbee.default_port_name = config.get('radio', 'default_port_name', 'serial')
    manager.xbee = xbee

    manager.run()

