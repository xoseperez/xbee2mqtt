#! /usr/bin/python
# -*- utf-8 -*-
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

__app__ = "Xbee to MQTT gateway"
__version__ = '0.2'
__author__ = "Xose Perez"
__copyright__ = "Copyright (C) Xose Perez"
__license__ = 'TBD'

import sys
import time
from datetime import datetime

#from tests.dummy_serial import Serial
from serial import Serial
from libs.Daemon import Daemon
from libs.Router import Router
from libs.Processor import Processor
from libs.Config import Config
from libs.Mosquitto import Mosquitto
from libs.XBee import XBee

class Broker(Daemon):

    debug = True
    duplicate_check_window = 5

    xbee = None
    mqtt = None
    router = None
    processor = None

    _topics = {}

    def log(self, message):
        if self.debug:
            timestamp = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f')
            sys.stdout.write("[%s] %s\n" % (timestamp, message))
            sys.stdout.flush()

    def cleanup(self):
        self.xbee.disconnect()
        self.mqtt_disconnect()
        self.log("[INFO] Exiting")
        sys.exit()

    def mqtt_connect(self):
        self.mqtt.connect()
        self.mqtt.on_connect = self.mqtt_on_connect
        self.mqtt.on_disconnect = self.mqtt_on_disconnect
        self.mqtt.on_message = self.mqtt_on_message

    def mqtt_disconnect(self):
        self.mqtt.disconnect()

    def mqtt_on_connect(self, obj, result_code):
        if result_code == 0:
            self.log("[INFO] Connected to Mosquitto broker")
            self.mqtt.send_connected()
        else:
            self.stop()

    def mqtt_on_disconnect(self, obj, result_code):
        if result_code != 0:
            time.sleep(5)
            self.mqtt_connect()

    def mqtt_on_message(self, msg):
        None

    def xbee_on_message(self, address, port, value):
        self.log("[DEBUG] %s %s %s" % (address, port, value))
        topic = self.router.forward(address, port)
        if topic:

            now = time.time()
            if topic in self._topics.keys() \
                and self._topics[topic]['time'] + self.duplicate_check_window > now \
                and self._topics[topic]['value'] == value \
                :
                    self.log("[DEBUG] Duplicate removed")
                    return
            self._topics[topic] = {'time': now, 'value': value}

            value = self.processor.map(topic, value)
            self.log("[MESSAGE] %s %s" % (topic, value))
            self.mqtt.publish(topic, value)

    def xbee_connect(self):
        self.log("[INFO] Connecting to Xbee")
        if not xbee.connect():
            self.stop()

    def run(self):

        self.log("[INFO] Starting " + __app__ + " v" + __version__)
        self.xbee.on_message = self.xbee_on_message
        self.xbee.log = self.log
        self.mqtt_connect()
        self.xbee_connect()

        while True:
            time.sleep(1)
            self.mqtt.loop()

if __name__ == "__main__":

    config = Config('xbee2mqtt.yaml')

    broker = Broker(config.get('daemon', 'pidfile', '/tmp/xbee2mqtt.pid'))
    broker.stdout = config.get('daemon', 'stdout', '/dev/null')
    broker.stderr = config.get('daemon', 'stderr', '/dev/null')
    broker.debug = config.get('daemon', 'debug', False)
    broker.duplicate_check_window = config.get('daemon', 'duplicate_check_window', 5)

    serial = Serial(
        config.get('radio', 'port', '/dev/ttyUSB0'),
        config.get('radio', 'baudrate', 9600)
    )

    xbee = XBee()
    xbee.serial = serial
    xbee.default_port_name = config.get('radio', 'default_port_name', 'serial')
    broker.xbee = xbee

    mqtt = Mosquitto(config.get('mqtt', 'client_id', 'xbee'))
    mqtt.host = config.get('mqtt', 'host', 'localhost')
    mqtt.port = config.get('mqtt', 'port', 1883)
    mqtt.keepalive = config.get('mqtt', 'keepalive', 60)
    mqtt.clean_session = config.get('mqtt', 'clean_session', False)
    mqtt.qos = config.get('mqtt', 'qos', 0)
    mqtt.retain = config.get('mqtt', 'retain', True)
    mqtt.status_topic = config.get('mqtt', 'status_topic', '/gateway/xbee/status')
    mqtt.set_will = config.get('mqtt', 'set_will', False)
    broker.mqtt = mqtt

    router = Router()
    router.default_topic_pattern = config.get('router', 'default_topic_pattern', '/raw/xbee/%s/%s')
    router.publish_undefined_topics = config.get('router', 'publish_undefined_topics', True)
    router.load(config.get('router', 'routes', []))
    broker.router = router

    processor = Processor()
    processor.load(config.get('processor', 'filters', []))
    broker.processor = processor

    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            broker.start()
        elif 'stop' == sys.argv[1]:
            broker.stop()
        elif 'restart' == sys.argv[1]:
            broker.restart()
        else:
            print "Unknown command"
            sys.exit(2)
        sys.exit(0)
    else:
        print "usage: %s start|stop|restart" % sys.argv[0]
        sys.exit(2)

