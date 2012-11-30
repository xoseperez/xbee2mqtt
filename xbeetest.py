#! /usr/bin/python

"""
receive_samples_async.py

Original by
Paul Malmsten, 2010
pmalmsten@gmail.com

This example reads the serial port and asynchronously processes IO data
received from a remote XBee.
"""

import time
#import serial
import dummy_serial as serial
from datetime import datetime

from xbee import XBee

PORT = '/dev/ttyUSB0'
BAUD_RATE = 9600

# buffer for device messages
buffer = dict()

def message_received(packet):

    device = packet['source_addr_long']
    frame_id = int(packet['frame_id'])

    # Data sent through the serial connection of the remote radio
    if (frame_id == 90):

        # Some streams arrive split in different packets
        # we buffer the data until we get an EOL
        buffer[device] = buffer.get(device,'') + packet['data']
        count = buffer[device].count('\n')
        if (count):
            lines = buffer[device].splitlines()
            try:
                buffer[device] = lines[count:][0]
            except:
                buffer[device] = ''
            for line in lines[:count]:
                line = line.rstrip()
                try:
                    sensor, value = line.split(':', 1)
                except:
                    value = line
                    sensor = 'serial'
                log(device, sensor, value)

    # Data received from an IO data sample
    if (frame_id == 92):
        for sensor, value in packet['samples'].iteritems():
            if sensor[:3] == 'dio':
                value = '1' if value else '0'
            log(device, sensor, value)

def log(device, sensor, value):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    print "[%s] %s @ %s = %s" % (timestamp, sensor if sensor is not None else 'serial', device, value)

# serial port
ser = serial.Serial(PORT, BAUD_RATE)

# create API object, which spawns a new thread
xbee = XBee(ser, callback=message_received)

# do other stuff in the main thread
while True:
    try:
        time.sleep(.1)
    except KeyboardInterrupt:
        break

# halt() must be called before closing the serial
# port in order to ensure proper thread shutdown
xbee.halt()
ser.close()
