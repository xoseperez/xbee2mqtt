#! /usr/bin/python
# -*- coding: utf-8 -*-
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

#   Copyright (C) 2013 by Xose Pérez
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
__copyright__ = "Copyright (C) 2013 Xose Pérez"
__license__ = 'GPL v3'

from mosquitto import Mosquitto
import ctypes
import time
import logging

# Class messages
MSG_CONNECTED = 1
MSG_DISCONNECTED = 2

class MosquittoWrapper(Mosquitto):
    """
    Wrapper for the official Mosquitto client that allows injection and easy mocking
    """

    host = 'localhost'
    port = 1883
    keepalive = 60
    qos = 0
    retain = False
    set_will = True

    status_topic = '/service/%s/status'
    subscribe_to = []

    connected = False
    logger = None

    on_message_cleaned = None

    _subscriptions = {}

    def log(self, level, message):
        if self.logger:
            self.logger.log(level, message)

    def connect(self):
        """
        Connects to the Mosquitto broker with the pre-configured parameters
        """
        self.on_connect = self._on_connect
        self.on_message = self._on_message
        self.on_disconnect = self._on_disconnect
        self.on_subscribe = self._on_subscribe
        self.on_log = self._on_log
        if self.set_will:
            self.will_set(self.status_topic % self._client_id, "0", self.qos, self.retain)
        self.log(logging.INFO, "Connecting to MQTT broker")
        Mosquitto.connect(self, self.host, self.port, self.keepalive)

    def subscribe(self, topics):
        """
        Publishes a value to a given topic, uses pre-loaded values for QoS and retain
        """
        if not isinstance(topics, list):
            topics = [topics]
        for topic in topics:
            rc, mid = Mosquitto.subscribe(self, topic, 0)
            self._subscriptions[mid] = topic
            self.log(logging.INFO, "Sent subscription request to topic %s" % topic)

    def publish(self, topic, value, qos=None, retain=None):
        """
        Publishes a value to a given topic, uses pre-loaded values for QoS and retain
        """
        qos = qos if qos is not None else self.qos
        retain = retain if retain is not None else self.retain
        Mosquitto.publish(self, topic, str(value), qos, retain)

    def _on_connect(self, mosq, obj, rc):
        """
        Callback when connection to the MQTT broker has succedeed or failed
        """
        if rc == 0:
            self.log(logging.INFO , "Connected to MQTT broker")
            self.publish(self.status_topic % self._client_id, "1")
            self.subscribe(self.subscribe_to)
            self.connected = True
        else:
            self.log(logging.ERROR , "Could not connect to MQTT broker")
            self.connected = False

    def _on_disconnect(self, mosq, obj, rc):
        """
        Callback when disconnecting from the MQTT broker
        """
        self.connected = False
        self.log(logging.INFO, "Disconnected from MQTT broker")
        if rc != 0:
            time.sleep(3)
            self.connect()

    def _on_message(self, mosq, obj, msg):
        """
        Incoming message
        """
        if self.on_message_cleaned:
            try:
                message = ctypes.string_at(msg.payload, msg.payloadlen)
            except:
                message = msg.payload
            self.on_message_cleaned(msg.topic, message)

    def _on_subscribe(self, mosq, obj, mid, qos_list):
        """
        Callback when succeeded subscription
        """
        topic = self._subscriptions.get(mid, 'Unknown')
        self.log(logging.INFO, "Subscription to topic %s confirmed" % topic)

    def _on_log(self, mosq, obj, level, string):
        self.log(logging.DEBUG, string)


if __name__ == '__main__':

    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)

    mqtt = MosquittoWrapper('mosquitto_test_client_2')
    mqtt.subscribe_to = ['/test']
    mqtt.logger = logger
    mqtt.connect()

    rc = 0
    while rc == 0:
        rc = mqtt.loop()
    print("rc: "+str(rc))

