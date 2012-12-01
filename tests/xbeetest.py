#! /usr/bin/python

import os,sys
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir)

import time
from datetime import datetime

from dummy_serial import Serial
#from serial import Serial
from xbee import XBee
from xbee2mqtt import Mapper, Config

PORT = '/dev/ttyUSB0'
BAUD_RATE = 9600

def log(topic, value):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    print "[%s] %s = %s" % (timestamp, topic, value)

# config
config = Config('../xbee2mqtt.yaml')

# mapper
mapper = Mapper()
mapper.on_message = log
mapper.mappings = config.get('mapper', 'mappings', [])

# serial port
serial = Serial(PORT, BAUD_RATE)

# create API object, which spawns a new thread
xbee = XBee(serial, callback=mapper.process)

# do other stuff in the main thread
while True:
    try:
        time.sleep(.1)
    except KeyboardInterrupt:
        break

# halt() must be called before closing the serial
# port in order to ensure proper thread shutdown
xbee.halt()
serial.close()
