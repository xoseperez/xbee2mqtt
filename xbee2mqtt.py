#! /usr/bin/python
# -*- utf-8 -*-
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

__author__ = "Xose Perez"
__copyright__ = "Copyright (C) Xose Perez"

import sys
import time
import serial

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
    xbee_topic_pattern = '/raw/%s/%s'
    xbee_default_sensor_name = 'UART'

    buffer = dict()

    def cleanup(self, signum, frame):
        self.xbee_disconnect()
        self.mqtt_disconnect()
        sys.exit()

    def mqtt_connect(self):
        self.mqtt.will_set("/client/%s/status" % self.mqtt_client_id, "Offline", self.mqtt_qos, self.mqtt_retain)
        self.mqtt.connect(self.mqtt_host, self.mqtt_port, self.mqtt_keepalive, self.mqtt_clean_session)
        self.mqtt.on_connect = self.mqtt_on_connect
        self.mqtt.on_disconnect = self.mqtt_on_disconnect
        self.mqtt.on_message = self.mqtt_on_message

    def mqtt_disconnect(self):
        self.mqtt.disconnect()

    def mqtt_send_message(self, topic, value):
        self.mqtt.publish(topic, value, self.mqtt_qos, self.mqtt_retain)

    def mqtt_on_connect(self, obj, result_code):
        if result_code == 0:
            self.mqtt_send_message("/client/%s/status" % self.mqtt_client_id, "Online")
        else:
            self.stop()

    def mqtt_on_disconnect(self, obj, result_code):
        if result_code != 0:
            time.sleep(5)
            self.mqtt_connect()

    def mqtt_on_message(self, msg):
        None

    def xbee_connect(self):
        self.ser = serial.Serial(self.xbee_port, self.xbee_baudrate)
        self.xbee = XBee(self.ser, callback=self.xbee_on_message)

    def xbee_disconnect(self):
        self.xbee.halt()
        self.ser.close()

    def xbee_on_message(self, packet):
        device = packet['source_addr_long']
        frame_id = int(packet['frame_id'])
        data = packet['data']

        if (frame_id == 90):
            self.buffer[device] = self.buffer.get(device,'') + data
            lines = self.buffer[device].splitlines(True)
            if (lines.count > 1):
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

        self.mqtt = mosquitto.Mosquitto(self.mqtt_client_id)
        self.mqtt_connect()
        self.xbee_connect()

        while True:
            time.sleep(1)
            self.mqtt.loop()


if __name__ == "__main__":
    daemon = xbee2mqtt('/tmp/xbee2mqtt.pid')
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

