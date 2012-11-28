#! /usr/bin/python
# -*- utf-8 -*-
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

__author__ = "Xose Perez"
__copyright__ = "Copyright (C) Xose Perez"

import sys
import time
from datetime import datetime
import dummy_serial as serial
#import serial

import mosquitto
from xbee import XBee
from daemon import Daemon

class xbee2mqtt(Daemon):

    # MQTT params
    mqtt_client_id='xbee2mqtt'
    mqtt_host='localhost'
    mqtt_port=1883
    mqtt_keepalive=60
    mqtt_clean_session=False
    mqtt_qos=0
    mqtt_retain=True

    # XBEE parameters
    xbee_port = '/dev/ttyUSB0'
    xbee_baudrate = 9600
    xbee_topic_pattern = '/raw/xbee/%s/%s'
    xbee_default_sensor_name = 'SERIAL'

    buffer = dict()

    def log(self, message):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        sys.stdout.write("[%s] %s\n" % (timestamp, message))
        sys.stdout.flush()

    def cleanup(self, signum, frame):
        self.xbee_disconnect()
        self.mqtt_disconnect()
        self.log("Exiting")
        sys.exit()

    def mqtt_connect(self):
        self.mqtt.will_set("/gateway/%s/status" % self.mqtt_client_id, "0", self.mqtt_qos, self.mqtt_retain)
        self.mqtt.connect(self.mqtt_host, self.mqtt_port, self.mqtt_keepalive, self.mqtt_clean_session)
        self.mqtt.on_connect = self.mqtt_on_connect
        self.mqtt.on_disconnect = self.mqtt_on_disconnect
        self.mqtt.on_message = self.mqtt_on_message

    def mqtt_disconnect(self):
        self.mqtt.disconnect()

    def mqtt_send_message(self, topic, value):
        self.log("Message: %s %s" % (topic, value))
        self.mqtt.publish(topic, value, self.mqtt_qos, self.mqtt_retain)

    def mqtt_on_connect(self, obj, result_code):
        if result_code == 0:
            self.log("Connected to Mosquitto broker")
            self.mqtt_send_message("/gateway/%s/status" % self.mqtt_client_id, "1")
            self.xbee_connect()
        else:
            self.stop()

    def mqtt_on_disconnect(self, obj, result_code):
        if result_code != 0:
            time.sleep(5)
            self.mqtt_connect()

    def mqtt_on_message(self, msg):
        None

    def xbee_connect(self):
        self.log("Connecting to Xbee")
        self.ser = serial.Serial(self.xbee_port, self.xbee_baudrate)
        self.xbee = XBee(self.ser, callback=self.xbee_on_message)

    def xbee_disconnect(self):
        self.xbee.halt()
        self.ser.close()

    def xbee_on_message(self, packet):
        device = packet['source_addr_long']
        frame_id = int(packet['frame_id'])
        data = packet['data']

        # Data sent through the serial connection of the remote radio
        if (frame_id == 90):

            # Some streams arrive split in different packets
            # we buffer the data until we get an EOL
            self.buffer[device] = self.buffer.get(device,'') + data
            lines = (self.buffer[device] + '\n').splitlines(True)
            if (len(lines) > 1):
                self.buffer[device] = lines[-1:][0]
                lines = lines[:-1]
                for line in lines:
                    sensor, value = line.rstrip().split(':', 2)
                    if (value == None):
                        value = sensor
                        sensor = self.default_sensor_name
                    topic = self.xbee_topic_pattern % (device, sensor)
                    self.mqtt_send_message(topic, value)

    def run(self):

        self.log("Starting")
        self.mqtt = mosquitto.Mosquitto(self.mqtt_client_id)
        self.mqtt_connect()

        while True:
            time.sleep(1)
            self.mqtt.loop()


if __name__ == "__main__":
    daemon = xbee2mqtt('/tmp/xbee2mqtt.pid', stdout='/tmp/xbee2mqtt.log', stderr='/tmp/xbee2mqtt.err')
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            daemon.start()
        elif 'stop' == sys.argv[1]:
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        else:
            print "Unknown command"
            sys.exit(2)
        sys.exit(0)
    else:
        print "usage: %s start|stop|restart" % sys.argv[0]
        sys.exit(2)

