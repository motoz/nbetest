#! /usr/bin/python3
# -*- coding: utf-8 -*-
"""
    NBE to MQTT (c) 2021 e1z0
    NBE Protocol Reverse Engineering Copyright (C) 2013  Anders Nylund

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
from __future__ import print_function
from argparse import ArgumentParser
from protocol import Proxy
import simplejson as json
import os
import paho.mqtt.client as paho
import time

PASSWORD = '0123456789' # not necessary at all :)

def mqtt_topic(config,topic,val):
    client = paho.Client(config["mqtt_client_name"])
    client.connect(config["mqtt_server"],config["mqtt_port"])
    client.publish(config["mqtt_prefix"]+"/"+topic,val)

def query_boiler(config):
    print ("Making query to the pellet burner...")
    with Proxy.discover(PASSWORD, config["nbe_port"], config["nbe_serial"]) as proxy:
        for query in config["options"]:
          response = proxy.get(query)
          for item in response:
             val = item.split("=",1)
             #for debug purposes #print ("Key: %s => val: %s" % (val[0],val[1]))
             mqtt_topic(config,val[0],val[1])

def help():
    print ("Just a simple mqtt bridge that publishes pellet burner info data to mqtt")

def daemon():
    print ("daemon mode")
    curr_path = os.path.dirname(os.path.realpath(__file__))
    config_file = curr_path+"/config.json"
    print ("Checking if exists:",config_file)
    if (os.path.exists(config_file)):
      with open(config_file) as f:
        config = json.load(f)
        print ("Settings loaded...")
        while(not time.sleep(config["refresh_rate"])):
          try:
            query_boiler(config)
          except:
            print ("Maybe we got some interruption with pallet burner connection or something have failed, continuing anyways...")
    else:
      print ("Settings file "+config_file+" does not exist!")

if __name__ == '__main__':

    argparser = ArgumentParser()
    argparser.add_argument('-d','--daemon', default=None, action='store_true')
    args = argparser.parse_args()
    try:
      if args.daemon is None:
          help()
      else:
          daemon()
    except AttributeError:
      print ("too few arguments")




