# xbee2mqtt

This daemon will monitor a coordinator XBee connected to a serial port of the computer for incoming messages.
From version 0.3 it also support setting digital pins LOW or HIGH on remote radios.
The radio **must** be configured in API mode.

You can read about this utility in my blog: [XBee to MQTT gateway](http://tinkerman.eldiariblau.net/xbee-to-mqtt-gateway/ "XBee to MQTT gateway").

## Requirements

All requirements will be installed in the virtual environment by running

<pre>./do setup</pre>

from the project root. If you don't want to use the virtualenv, you will have to install
the requierements manually:

* Modified version of the python-xbee library. You can get the forked code here:
<pre>
hg clone https://code.google.com/r/xoseperez-python-xbee python-xbee
cd python-xbee
python setup.py install
</pre>

* python-yaml
<pre>apt-get install python-yaml</pre>

* python-mosquitto
<pre>apt-get install python-mosquitto</pre>

* python-serial
<pre>apt-get install python-serial</pre>


## Install

Just clone or extract the code in some folder. I'm not providing an setup.py file yet.
But you can install a local virtual environment using 

<pre>./do setup</pre>


## Configuration

Rename or copy the xbee2mqtt.yaml.sample to xbee2mqtt.yaml and edit it. The configuration is pretty straight forward:


### general

**duplicate_check_window** lets you define a time window in seconds where messages for the same topic and with the same value will be ignored as duplicates.
**default_topic_pattern** lets you define a default topic for every message. It accepts two placeholders: {address} for the radio address and {port}. 
The port can be the radio pin (dio12, adc1, adc7,...) or a string for messages sent through the UART of the sending radio. 
**routes** dictionary defines the topics map. 
Set **publish_undefined_topic** False to filter out topics not defined in the routes dictionary. 
If it's True and the route is not defined it will be mapped to a topic defined by the **default_topic_pattern**.
For every defined route a subscription to the same route plus "/set" will be done. 
If the route maps to a digital port in the remote radio you can change its status to OUTPUT LOW ot OUTPUT HIGH by publishing a 0 or a 1 to this topic.


### radio

Configuration of the port where the XBee is attached to.
All messages are defined by the originating radio address (an 8 byte value) and a port or pin.
The **default_port_name** parameter lets you define what port name to use when the message was originally sent through the UART interface of the originating radio 
To send a custom message just send "port:value\n" through the UART interface of the radio, if no port is specified the **default_port_name** value will be used.


### mqtt

These are standard Mosquitto parameters. The status topic is the topic to post messages when the daemon starts or stops.


### processor

The processor is responsible for pre-processing the values before publishing them. There are several filters defined in libs/Filters.py


## Running it

The util stays resident as a daemon. You can start it, stop it or restart it (to reload the configuration) by using:

<pre>python xbee2mqtt.py start|stop|restart</pre>

or easier (it will login the virtual enviroment and execute the previous command):

<pre>./do start</pre>




