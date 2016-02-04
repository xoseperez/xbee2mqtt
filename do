#!/bin/bash

FOLDER=.venv

if [ $# -eq 0 ]; then
    ACTION='activate'
else
    ACTION=$1
fi

case "$ACTION" in

    "activate")
        . venv/bin/activate
        ;;

    "deactivate")
        deactivate
        ;;

    "setup")
        if [ ! -d $FOLDER ]; then
            virtualenv $FOLDER
        fi

        deactivate
        source $FOLDER/bin/activate

        pip install ConfigParser
        pip install pyaml
        pip install pyserial
        pip install nose

        wget https://bitbucket.org/oojah/mosquitto/raw/v1.3/lib/python/mosquitto.py
        mv mosquitto.py $FOLDER/lib/python2.7/site-packages/

        hg clone https://xose.perez@code.google.com/r/xoseperez-python-xbee tmp
        cd tmp
        python setup.py install
        cd ..
        rm -rf tmp
        ;;

    "start" | "stop" | "restart")
        source $FOLDER/bin/activate
        python xbee2mqtt.py $ACTION
        deactivate
        ;;

    "tests")
        source $FOLDER/bin/activate
        .venv/bin/nosetests
        ;;

    *)
        echo "Unknown action $ACTION."
        ;;
esac


