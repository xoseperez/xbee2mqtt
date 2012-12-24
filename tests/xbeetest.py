#! /usr/bin/python

import os,sys
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir)

import time
from datetime import datetime

#from dummy_serial import Serial
from serial import Serial
from xbee import XBee
from xbee2mqtt import Gateway, Config
from libs.MessagePreprocessor import MessagePreprocessor

def log(response):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    publish = '(NOT PUBLISHED)' if response['publish'] == False else ''
    print "[%s] %s %s %s" % (timestamp, response['topic'], response['value'], publish)
    if response['publish'] and response['timestampable']:
        ts = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        print "[%s] %s %s" % (timestamp, response['topic'] + '/timestamp', ts)


# config
config = Config('../xbee2mqtt.yaml')

# processor
processor = MessagePreprocessor()
processor.default_topic_pattern = config.get('processor', 'default_topic_pattern', '/raw/xbee/%s/%s')
processor.publish_undefined_topics = config.get('processor', 'publish_undefined_topics', True)
processor.load_map(config.get('processor', 'mappings', []))

# gateway
gateway = Gateway()
gateway.default_port_name = config.get('gateway', 'default_port_name', 'serial')
gateway.processor = processor
gateway.on_message = log

# serial port
serial = Serial(
    config.get('radio', 'port', '/dev/ttyUSB0'),
    config.get('radio', 'baudrate', 9600)
)

# create API object, which spawns a new thread
xbee = XBee(serial, callback=gateway.process)

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
