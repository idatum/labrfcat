#!/usr/bin/env sh

# Mosquitto username and password for ACL restrictions,
# and FQDN host for TLS.
export MQTT_USERNAME=`cat .mosquitto_user`
export MQTT_PASSWORD=`cat .mosquitto_pwd`
export MQTT_HOST=`cat .mosquitto_host`

while true
do
    # expecting topic: rfcat/minka/{cmd}
    # where cmd defined in minka.py
    /usr/bin/env mosquitto_sub \
                  -u $MQTT_USERNAME -P $MQTT_PASSWORD \
                  -h $MQTT_HOST \
                  -p 8883 --capath /etc/ssl/certs/ \
                  -v -t "rfcat/minka/+" | while read msg
    do
        if [ -z "${msg}" ]
        then
            continue
        fi
        # stdout: topic + (null) payload
        cmd=`echo $msg | /usr/bin/env awk '{print $1}' | /usr/bin/awk -F '/' '{print $3}'`
        /usr/bin/env python minka.py --cmd=$cmd
    done
done
