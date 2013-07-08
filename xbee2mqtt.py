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
__version__ = "0.4.20130708"
__author__ = "Xose Pérez"
__contact__ = "xose.perez@gmail.com"
__copyright__ = "Copyright (C) 2012-2013 Xose Pérez"
__license__ = 'GPL v3'

import sys
import time
import logging

#from tests.SerialMock import Serial
from serial import Serial
from libs.daemon import Daemon
from libs.processor import Processor
from libs.config import Config
from libs.mosquitto_wrapper import MosquittoWrapper
from libs.xbee_wrapper import XBeeWrapper

class Xbee2MQTT(Daemon):
    """
    Xbee2MQTT daemon.
    Glues the different components together
    """

    debug = True
    duplicate_check_window = 5

    logger = None
    xbee = None
    mqtt = None
    processor = None

    _routes = {}
    _actions = {}
    _topics = {}

    def load(self, routes):
        """
        Read configuration and store bidirectional dicts
        """
        for address, ports in routes.iteritems():
            for port, topic in ports.iteritems():
                self._routes[(address, port)] = topic
                self._actions['%s/set' % topic] = (address, port)

    def log(self, level, message):
        if self.logger:
            self.logger.log(level, message)

    def cleanup(self):
        """
        Clean up connections and unbind ports
        """
        self.xbee.disconnect()
        self.log(logging.INFO, "Exiting")
        self.mqtt.disconnect()
        sys.exit()

    def mqtt_on_message(self, topic, message):
        """
        Message received from a subscribed topic
        """

        self.log(logging.DEBUG, "Message received from MQTT broker: %s %s" % (topic, message))

        data = self._actions.get(topic, None)
        if data:
            address, port = data
            self.log(logging.INFO, "Setting radio %s port %s to %s" % (address, port, message))
            try:
                self.xbee.send_message(address, port, message)
            except Exception as e:
                self.log(logging.ERROR, "Error while sending message (%e)" % e)


    def xbee_on_message(self, address, port, value):
        """
        Message from the radio coordinator
        """
        self.log(logging.DEBUG, "Message received from radio: %s %s %s" % (address, port, value))
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
                    self.log(logging.DEBUG, "Duplicate removed")
                    return
            self._topics[topic] = {'time': now, 'value': value}

            value = self.processor.process(topic, value)
            self.log(logging.INFO, "Sending message to MQTT broker: %s %s" % (topic, value))
            self.mqtt.publish(topic, value)

    def run(self):
        """
        Entry point, initiates components and loops forever...
        """
        self.log(logging.INFO, "Starting " + __app__ + " v" + __version__)
        self.mqtt.on_message_cleaned = self.mqtt_on_message
        self.mqtt.subscribe_to = self._actions.keys()
        self.mqtt.logger = self.logger
        self.xbee.on_message = self.xbee_on_message
        self.xbee.logger = self.logger

        self.mqtt.connect()
        if not self.xbee.connect():
            self.stop()

        while True:
            self.mqtt.loop()

if __name__ == "__main__":

    config = Config('config/xbee2mqtt.yaml')

    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    logger = logging.getLogger()
    logger.setLevel(config.get('daemon', 'logging_level', logging.INFO))
    logger.addHandler(handler)

    mqtt = MosquittoWrapper(config.get('mqtt', 'client_id', None))
    mqtt.host = config.get('mqtt', 'host', 'localhost')
    mqtt.port = config.get('mqtt', 'port', 1883)
    mqtt.keepalive = config.get('mqtt', 'keepalive', 60)
    mqtt.clean_session = config.get('mqtt', 'clean_session', False)
    mqtt.qos = config.get('mqtt', 'qos', 0)
    mqtt.retain = config.get('mqtt', 'retain', True)
    mqtt.set_will = config.get('mqtt', 'set_will', True)

    serial = Serial(
        config.get('radio', 'port', '/dev/ttyUSB0'),
        config.get('radio', 'baudrate', 9600)
    )
    xbee = XBeeWrapper()
    xbee.serial = serial
    xbee.default_port_name = config.get('radio', 'default_port_name', 'serial')

    processor = Processor(config.get('processor', 'filters', []))

    xbee2mqtt = Xbee2MQTT(config.get('general', 'pidfile', '/tmp/xbee2mqtt.pid'))
    xbee2mqtt.stdout = config.get('general', 'stdout', '/dev/null')
    xbee2mqtt.stderr = config.get('general', 'stderr', '/dev/null')
    xbee2mqtt.debug = config.get('general', 'debug', False)
    xbee2mqtt.duplicate_check_window = config.get('general', 'duplicate_check_window', 5)
    xbee2mqtt.default_topic_pattern = config.get('general', 'default_topic_pattern', '/raw/xbee/{address}/{port}')
    xbee2mqtt.publish_undefined_topics = config.get('general', 'publish_undefined_topics', True)
    xbee2mqtt.load(config.get('general', 'routes', {}))
    xbee2mqtt.logger = logger
    xbee2mqtt.mqtt = mqtt
    xbee2mqtt.xbee = xbee
    xbee2mqtt.processor = processor

    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            xbee2mqtt.start()
        elif 'stop' == sys.argv[1]:
            xbee2mqtt.stop()
        elif 'restart' == sys.argv[1]:
            xbee2mqtt.restart()
        else:
            print "Unknown command"
            sys.exit(2)
        sys.exit(0)
    else:
        print "usage: %s start|stop|restart" % sys.argv[0]
        sys.exit(2)

