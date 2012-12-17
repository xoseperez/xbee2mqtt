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
import yaml

#from tests.dummy_serial import Serial
from serial import Serial
from mosquitto import Mosquitto as _Mosquitto
from xbee import XBee
from libs.daemon import Daemon
from libs.MessagePreprocessor import MessagePreprocessor

class Mosquitto(_Mosquitto):

    client_id = 'xbee2mqtt'
    host = 'localhost'
    port = 1883
    keepalive = 60
    clean_session = False
    qos = 0
    retain = False
    status_topic = '/service/xbee2mqtt/status'

    def connect(self):
        self.will_set(self.status_topic, "0", self.qos, self.retain)
        _Mosquitto.connect(self, self.host, self.port, self.keepalive, self.clean_session)

    def publish(self, topic, value):
        _Mosquitto.publish(self, topic, str(value), self.qos, self.retain)

    def send_connected(self):
        self.publish(self.status_topic, "1")


class Gateway(object):

    default_port_name = 'serial'
    processor = None

    buffer = dict()

    def __init__(self):
        None

    def process(self, packet):

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
                    self.map(address, port, value)

        # Data received from an IO data sample
        if (frame_id == 92):
            for port, value in packet['samples'].iteritems():
                if port[:3] == 'dio':
                    value = '1' if value else '0'
                self.map(address, port, value)

    def load_map(self, map):
        for address, ports in map.iteritems():
            for port, value in ports.iteritems():
                try:
                    self.mapping[address, port] = value['topic']
                except:
                    self.mapping[address, port] = value

    def map(self, address, port, value):
        topic, value = self.processor.map(address, port, value)
        self.on_message(topic, value)

    def on_message(self, topic, value):
        None


class Broker(Daemon):

    debug = True
    serial = None
    gateway = None
    mqtt = None

    def log(self, message):
        if self.debug:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
            sys.stdout.write("[%s] %s\n" % (timestamp, message))
            sys.stdout.flush()

    def cleanup(self, signum, frame):
        self.xbee_disconnect()
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

    def mqtt_send_message(self, topic, value):
        self.log("[MESSAGE] %s %s" % (topic, value))
        self.mqtt.publish(topic, value)

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

    def xbee_connect(self):
        self.log("[INFO] Connecting to Xbee")
        try:
            self.xbee = XBee(self.serial, callback=self.gateway.process)
        except:
            self.stop()

    def xbee_disconnect(self):
        self.xbee.halt()
        self.serial.close()

    def run(self):

        self.log("[INFO] Starting " + __app__ + " v" + __version__)
        self.gateway.on_message = self.mqtt_send_message
        self.mqtt_connect()
        self.xbee_connect()

        while True:
            time.sleep(1)
            self.mqtt.loop()

class Config(object):

    config = None

    def __init__(self, filename):
        handler = file(filename, 'r')
        self.config = yaml.load(handler)
        handler.close()

    def get(self, section, key, default=None):
        response = default
        if self.config.has_key(section):
            if self.config[section].has_key(key):
                response = self.config[section][key]
        return response

if __name__ == "__main__":

    config = Config('xbee2mqtt.yaml')

    broker = Broker(config.get('daemon', 'pidfile', '/tmp/xbee2mqtt.pid'))
    broker.stdout = config.get('daemon', 'stdout', '/dev/null')
    broker.stderr = config.get('daemon', 'stderr', '/dev/null')
    broker.debug = config.get('daemon', 'debug', False)

    serial = Serial(
        config.get('radio', 'port', '/dev/ttyUSB0'),
        config.get('radio', 'baudrate', 9600)
    )
    broker.serial = serial

    mqtt = Mosquitto(config.get('mqtt', 'client_id', 'xbee'))
    mqtt.host = config.get('mqtt', 'host', 'localhost')
    mqtt.port = config.get('mqtt', 'port', 1883)
    mqtt.keepalive = config.get('mqtt', 'keepalive', 60)
    mqtt.clean_session = config.get('mqtt', 'clean_session', False)
    mqtt.qos = config.get('mqtt', 'qos', 0)
    mqtt.retain = config.get('mqtt', 'retain', True)
    mqtt.status_topic = config.get('mqtt', 'status_topic', '/gateway/xbee/status')
    broker.mqtt = mqtt

    processor = MessagePreprocessor()
    processor.default_topic_pattern = config.get('processor', 'default_topic_pattern', '/raw/xbee/%s/%s')
    processor.load_map(config.get('processor', 'mappings', []))

    gateway = Gateway()
    gateway.default_port_name = config.get('gateway', 'default_port_name', 'serial')
    gateway.processor = processor

    broker.gateway = gateway

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

