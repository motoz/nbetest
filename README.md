# Test program and mqtt bridge for the NBE pellet burner UDP protocol

A client that can connect to a scotte V7/V13 controller (and apparently also aduro pellet hybrid stoves), and a test server that simulates a controller box.


## MQTT Bridge

<pre>
python mqtt-bridge.py -d
</pre>

Configuration lies in config.json, just modify to suit your needs also edit and copy pellet.service to /etc/systemd/system and start daemon
```
systemctl enable pellet&& systemctl start pellet
```

## MQTT Bridge using docker

```
make up (edit docker-compose.yml before)
```

## Home Assistant Integration

Just copy [pellet-burner.yaml](/pellet-burner.yaml) to your home assistant config directory and include in the main configuration.yaml file.
```
sensor: !include pellet-burner.yaml
```
You will have to restart Home Assistant.

<img src="https://github.com/e1z0/nbetest/raw/master/pics/pellet_burner_ha_info_pic.png" width=40% height=40%>


## Client

<pre>
    python client.py -h
    usage: client.py [-h] [-v] [-a ADDRESS] [-p PASSWORD]
                     {raw,set,get} ...

    positional arguments:
      {raw,set,get}         sub-command help
        raw
        set                 write item value
        get                 get all items

    optional arguments:
      -h, --help            show this help message and exit
      -v, --verbose
      -a ADDRESS, --address ADDRESS
                            controller address, autodiscovered if omitted
      -p PASSWORD, --password PASSWORD
      -s SERIAL, --serial SERIAL

examples:

python client.py get
settings/
operating_data/
advanced_data/
consumption_data/
event_log/
sw_versions/
info/

python client.py get settings
settings/boiler/
settings/hot_water/
settings/regulation/
settings/weather/
settings/oxygen/
settings/cleaning/
settings/hopper/
settings/fan/
settings/auger/
settings/ignition/
settings/pump/
settings/sun/
settings/vacuum/
settings/misc/
settings/alarm/
settings/manual/
settings/bbq_smoke/
settings/bbq_rotation/
settings/bbq_grill/
settings/bbq_meat/
settings/bbq_afterburner/
settings/bbq_div/

python client.py -s 765432 -get settings/boiler/temp
77

python client.py -s 765432 -p 3625476689 set settings/boiler/temp 78
OK

</pre>


## Pycrypto library

install with

    pip install pycrypto

pyCryptoDome doesn't work
