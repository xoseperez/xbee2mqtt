#! /usr/bin/python

import os,sys
parentdir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0,parentdir)

import time
from datetime import datetime

from dummy_serial import Serial
#from serial import Serial
from libs.XBee import XBee
from libs.Config import Config
from libs.Router import Router
from libs.Processor import Processor

def log(address, port, value):
    topic = router.forward(address, port)
    value = processor.map(topic, value)
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    print "[%s] %s %s %s %s" % (timestamp, address, port, topic, value)

# config
config = Config('../xbee2mqtt.yaml')

# Router
router = Router()
router.default_topic_pattern = config.get('router', 'default_topic_pattern', '/raw/xbee/%s/%s')
router.publish_undefined_topics = config.get('router', 'publish_undefined_topics', True)
router.load(config.get('router', 'routes', []))

# Processor
processor = Processor()
processor.load(config.get('processor', 'filters', []))

# serial port
serial = Serial(
    config.get('radio', 'port', '/dev/ttyUSB0'),
    config.get('radio', 'baudrate', 9600)
)

# xbee
xbee = XBee()
xbee.default_port_name = config.get('radio', 'default_port_name', 'serial')
xbee.serial = serial
xbee.on_message = log
xbee.connect()

# do other stuff in the main thread
while True:
    try:
        time.sleep(.1)
    except KeyboardInterrupt:
        break

xbee.disconnect()
