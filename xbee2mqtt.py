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

__app__ = "Xbee to MQTT gateway"
__version__ = "0.3"
__author__ = "Xose Pérez"
__contact__ = "xose.perez@gmail.com"
__copyright__ = "Copyright (C) 2012-2013 Xose Pérez"
__license__ = 'GPL v3'

import sys
import time
import ctypes
from datetime import datetime

#from tests.SerialMock import Serial
from serial import Serial
from libs.Daemon import Daemon
from libs.Processor import Processor
from libs.Config import Config
from libs.Mosquitto import Mosquitto
from libs.XBee import XBee

class Xbee2MQTT(Daemon):
    """
    Xbee2MQTT daemon.
    Glues the different components together
    """

    debug = True
    duplicate_check_window = 5

    xbee = None
    mqtt = None
    processor = None

    _routes = {}
    _actions = {}

    def load(self, routes):
        """
        Read configuration and store bidirectional dicts
        """
        for address, ports in routes.iteritems():
            for port, topic in ports.iteritems():
                self._routes[(address, port)] = topic
                self._actions['%s/set' % topic] = (address, port)

    def log(self, message):
        """
        Log method.
        TODO: replace with standard python logging facility
        """
        if self.debug:
            timestamp = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')
            sys.stdout.write("[%s] %s\n" % (timestamp, message))
            sys.stdout.flush()

    def cleanup(self):
        """
        Clean up connections and unbind ports
        """
        self.xbee.disconnect()
        self.mqtt.disconnect()
        self.log("[INFO] Exiting")
        sys.exit()

    def mqtt_connect(self):
        """
        Initiate connection to MQTT broker and bind callback methods
        """
        self.mqtt.connect()
        self.mqtt.on_connect = self.mqtt_on_connect
        self.mqtt.on_disconnect = self.mqtt_on_disconnect
        self.mqtt.on_message = self.mqtt_on_message
        self.mqtt.on_subscribe = self.mqtt_on_subscribe

    def mqtt_on_connect(self, obj, result_code):
        """
        Callback when connection to the MQTT broker has succedeed or failed
        """
        if result_code == 0:
            self.log("[INFO] Connected to Mosquitto manager")
            self.mqtt.send_connected()
            for topic in self._actions:
                rc, mid = self.mqtt.subscribe(topic, 0)
                self.log("[INFO] Subscription to %s sent with MID %d" % (topic, mid))
        else:
            self.stop()

    def mqtt_on_disconnect(self, obj, result_code):
        """
        Callback when disconnecting from the MQTT broker
        """
        if result_code != 0:
            time.sleep(5)
            self.mqtt_connect()

    def mqtt_on_subscribe(self, obj, mid, qos_list):
        """
        Callback when succeeded subscription
        """
        self.log("[INFO] Subscription for MID %s confirmed." % mid)

    def mqtt_on_message(self, obj, msg):
        """
        Message received from a subscribed topic
        """
        data = self._actions.get(msg.topic, None)
        if data:
            address, port = data
            try:
                message = ctypes.string_at(msg.payload, msg.payloadlen)
            except:
                message = msg.payload

            self.log("[DEBUG] Setting radio %s port %s to %s" % (address, port, message))
            self.xbee.send_message(address, port, message)

    def xbee_on_message(self, address, port, value):
        """
        Message from the radio coordinator
        """
        self.log("[DEBUG] %s %s %s" % (address, port, value))
        topic = self._routes.get(
            (address, port),
            self.default_topic_pattern.format(address=address, port=port) if self.publish_undefined_topics else False
        )
        if topic:

            now = time.time()
            if topic in self._topics.keys() \
                and self._topics[topic]['time'] + self.duplicate_check_window > now \
                and self._topics[topic]['value'] == value \
                :
                    self.log("[DEBUG] Duplicate removed")
                    return
            self._topics[topic] = {'time': now, 'value': value}

            value = self.processor.process(topic, value)
            self.log("[MESSAGE] %s %s" % (topic, value))
            self.mqtt.publish(topic, value)

    def xbee_connect(self):
        """
        Initiate connection to the radio coordinator via serial port
        """
        self.log("[INFO] Connecting to Xbee")
        if not self.xbee.connect():
            self.stop()
        self.xbee.on_message = self.xbee_on_message

    def run(self):
        """
        Entry point, initiates components and loops forever...
        """
        self.log("[INFO] Starting " + __app__ + " v" + __version__)
        #self.xbee.log = self.log
        self.mqtt_connect()
        self.xbee_connect()

        while True:
            self.mqtt.loop()

if __name__ == "__main__":

    config = Config('xbee2mqtt.yaml')

    manager = Xbee2MQTT(config.get('general', 'pidfile', '/tmp/xbee2mqtt.pid'))
    manager.stdout = config.get('general', 'stdout', '/dev/null')
    manager.stderr = config.get('general', 'stderr', '/dev/null')
    manager.debug = config.get('general', 'debug', False)
    manager.duplicate_check_window = config.get('general', 'duplicate_check_window', 5)
    manager.default_topic_pattern = config.get('general', 'default_topic_pattern', '/raw/xbee/{address}/{port}')
    manager.publish_undefined_topics = config.get('general', 'publish_undefined_topics', True)
    manager.load(config.get('general', 'routes', {}))

    serial = Serial(
        config.get('radio', 'port', '/dev/ttyUSB0'),
        config.get('radio', 'baudrate', 9600)
    )

    xbee = XBee()
    xbee.serial = serial
    xbee.default_port_name = config.get('radio', 'default_port_name', 'serial')
    manager.xbee = xbee

    mqtt = Mosquitto(config.get('mqtt', 'client_id', 'xbee'))
    mqtt.host = config.get('mqtt', 'host', 'localhost')
    mqtt.port = config.get('mqtt', 'port', 1883)
    mqtt.keepalive = config.get('mqtt', 'keepalive', 60)
    mqtt.clean_session = config.get('mqtt', 'clean_session', False)
    mqtt.qos = config.get('mqtt', 'qos', 0)
    mqtt.retain = config.get('mqtt', 'retain', True)
    mqtt.status_topic = config.get('mqtt', 'status_topic', '/gateway/xbee/status')
    mqtt.set_will = config.get('mqtt', 'set_will', False)
    manager.mqtt = mqtt

    processor = Processor(config.get('processor', 'filters', []))
    manager.processor = processor

    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            manager.start()
        elif 'stop' == sys.argv[1]:
            manager.stop()
        elif 'restart' == sys.argv[1]:
            manager.restart()
        else:
            print "Unknown command"
            sys.exit(2)
        sys.exit(0)
    else:
        print "usage: %s start|stop|restart" % sys.argv[0]
        sys.exit(2)

