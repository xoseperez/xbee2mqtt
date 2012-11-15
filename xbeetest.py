#! /usr/bin/python

"""
receive_samples_async.py

By Paul Malmsten, 2010
pmalmsten@gmail.com

This example reads the serial port and asynchronously processes IO data
received from a remote XBee.
"""

import time
import serial
from datetime import datetime

from xbee import XBee

PORT = '/dev/ttyUSB0'
BAUD_RATE = 9600

# buffer for device messages
buffer = dict()

def message_received(packet):
    device = packet['source_addr_long']
    frame_id = int(packet['frame_id'])
    data = packet['data']
    process(device, frame_id, data)

def process(device, frame_id, data):
    if (frame_id == 90):
        buffer[device] = buffer.get(device,'') + data
        lines = buffer[device].splitlines(True)
        if (lines.count > 1):
            buffer[device] = lines[-1:][0]
            lines = lines[:-1]
            for line in lines:
                if (line.find(':') > -1):
                    try:
                        sensor, value = line.split(':', 2)
                    except:
                        sensor = None
                        value = line
                else:
                    sensor = None
                    value = line
                save(device, sensor, value.rstrip())

def save(device, sensor, value):
    log(device, sensor, value)

def log(device, sensor, value):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    print "[%s] %s @ %s = %s" % (timestamp, sensor if sensor is not None else 'DEFAULT', device, value)

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
