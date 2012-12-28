#! /usr/bin/python
# -*- utf-8 -*-
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

from mosquitto import Mosquitto as _Mosquitto

class Mosquitto(_Mosquitto):

    client_id = 'xbee2mqtt'
    host = 'localhost'
    port = 1883
    keepalive = 60
    clean_session = False
    qos = 0
    retain = False
    status_topic = '/service/xbee2mqtt/status'
    set_will = False

    def connect(self):
        if self.set_will:
            self.will_set(self.status_topic, "0", self.qos, self.retain)
        _Mosquitto.connect(self, self.host, self.port, self.keepalive, self.clean_session)

    def publish(self, topic, value):
        _Mosquitto.publish(self, topic, str(value), self.qos, self.retain)

    def send_connected(self):
        self.publish(self.status_topic, "1")


