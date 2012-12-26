#! /usr/bin/python
# -*- utf-8 -*-
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

from xbee import XBee as _XBee

class XBee(object):

    default_port_name = 'serial'

    serial = None
    xbee = None

    buffer = dict()

    def disconnect(self):
        self.xbee.halt()
        self.serial.close()
        return True

    def connect(self):
        try:
            self.xbee = _XBee(self.serial, callback=self.process)
        except:
            return False
        return True

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
                    self.on_message(address, port, value)

        # Data received from an IO data sample
        if (frame_id == 92):
            for port, value in packet['samples'].iteritems():
                if port[:3] == 'dio':
                    value = 1 if value else 0
                self.on_message(address, port, value)

    def on_message(self, address, port, value):
        None

