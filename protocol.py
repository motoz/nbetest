#! /usr/bin/python
# -*- coding: utf-8 -*-
"""
    Copyright (C) 2013  Anders Nylund

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
import socket
from random import randrange
import time
from Crypto.PublicKey import RSA
import base64
from frames import Request_frame, Response_frame
from os import urandom
from random import SystemRandom, randrange
import select
#import xtea

class Proxy:
    root = ('settings', 'operating_data', 'advanced_data', 'consumption_data', 'event_log','sw_versions','info')
    settings = ('boiler', 'hot_water', 'regulation', 'weather', 'weather2', 'oxygen', 'cleaning', 'hopper', 'fan', 'auger', 'ignition', 'pump', 
        'sun', 'vacuum', 'misc', 'alarm', 'manual')
    consumption_data = ('total_hours', 'total_days', 'total_months', 'total_years', 'dhw_hours', 'dhw_days', 'dhw_months', 'dhw_years', 'counter')

    def __init__(self, password, port=8483, addr=None, serialnumber=None):
        self.password = password
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        for p in range(port+1, 9999):
            try:
                s.bind(('', p))
                break
            except socket.error:
                if p==9999:
                    print ('No free port found')
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if addr == '<broadcast>':
            s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.settimeout(0.5)
        self.s = s
        request = Request_frame()
        self.response = Response_frame(request)

        request.function = 0
        request.payload = 'NBE Discovery'
        if serialnumber:
            request.controllerid = serialnumber
        request.sequencenumber = randrange(0,100)
        self.s.sendto(request.encode() , (addr, port))
        self.s.settimeout(5.0)
        data, server = self.s.recvfrom(4096)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 0)
        self.addr = server

        self.response.decode(data)
        res = self.response.parse_payload()
        if 'Serial' in res:
            self.serial = res['Serial']
        if 'IP' in res:
            self.ip = res['IP']

        request.payload = 'misc.rsa_key'
        request.function = 1
        request.sequencenumber += 1
        self.s.sendto(request.encode() , self.addr)
        self.s.settimeout(5.0)
        data, server = self.s.recvfrom(4096)
        self.response.decode(data)
        try:
            key = self.response.payload.split('rsa_key=')[1]
            key = base64.b64decode(key)
            request.public_key = RSA.importKey(key)
        except IOError: #Exception as e:
            request.public_key = None
        request.pincode = self.password
        self.request = request

    def get(self, d=None):
        d = d.rstrip('/').split('/')
        if d[0] == None or d[0] == '*':
            return [p + '/' for p in self.root]
        elif d[0] == 'settings':
            if len(d) == 1:
                return ['settings/%s/'%s for s in self.settings]
            elif d[1] in self.settings:
                if len(d) == 2:
                    response = self.make_request(1, d[1] + '.*')
                    return ['settings/%s/%s'%(d[1], s) for s in response.payload.split(';')]
                else:
                    response = self.make_request(1, d[1] + '.' + d[2])
                    try:
                        return (response.payload.split('=', 1)[1],)
                    except IndexError:
                        return (response.payload,)
            else:
                return []
        elif d[0] in ('operating_data', 'advanced_data'):
            if d[0] == 'operating_data':
                f = 4
            else:
                f = 5
            if len(d) == 1:
                response = self.make_request(f, '*')
                return [d[0] + '/' + s for s in response.payload.split(';')]
            elif len(d) == 2:
                response = self.make_request(f, d[1])
                try:
                    return (response.payload.split('=')[1],)
                except IndexError:
                    return (response.payload,)
        elif d[0] == 'consumption_data':
            if len(d) == 1:
                return [d[0] + '/' + s for s in self.consumption_data]
            elif d[1] in self.consumption_data:
                response = self.make_request(6, d[1])
                return [d[0] + '/' + s for s in response.payload.split(';')]
            else:
                return []
        elif d[0] == 'sw_versions':
            if len(d) == 1:
                response = self.make_request(10, '')
                return [s for s in response.payload.split(';')]
            else:
                return []
        elif d[0] == 'info':
            if len(d) == 1:
                response = self.make_request(9, '')
                return [s for s in response.payload.split(';')]
            else:
                return []
        elif d[0] == 'event_log':
            if len(d) == 1:
                now = time.strftime('%y%m%d:%H%M%S;',time.localtime())
                response = self.make_request(8, now)
                return response.payload.split(';')
            else:
                response = self.make_request(8, d[1])
                return response.payload.split(';')

    def set(self, path=None, value=None):
        d = path.rstrip('/').split('/')
        if d[0] == None or d[0] == '*':
            return ('settings',)
        elif len(d) == 3 and d[1] in self.settings and value is not None :
            self.s.settimeout(5)
            response = self.make_request(2, '.'.join(d[1:3]) + '=' + value, encrypt=True)
            self.s.settimeout(1.3)
            if response.status == 0:
                return ('OK',)
            else:
                return (response.payload,)
        else:
            return self.get(path)

    @classmethod
    def discover(cls, password, port, serialnumber):
        return cls(password, port, addr='<broadcast>', serialnumber=serialnumber)

    def make_request(self, function, payload, encrypt=False, key=None):
        #print(' '.join([hex(ord(ch)) for ch in c.framedata]))
        self.request.sequencenumber += 1
        self.request.payload = payload
        self.request.function = function
        self.request.encrypted = encrypt
        self.request.pincode = self.password
        self.s.sendto(self.request.encode(), self.addr)
        # needs to implement poll wait
        self.s.settimeout(5.0)
        ready = select.select([self.s], [], [], 5)
        if ready[0]:
          data, server = self.s.recvfrom(4096)
          self.response.decode(data)
          return self.response

    def __enter__(self):
        return self

    def __exit__(self, password, port=8483, addr=None, serialnumber=None):
        self.s.close()

class Controller:
    def __init__(self, host, password, port=1900, seqnums=True):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.bind((host, port))
        self.password = password
        self.request = V3_request_frame()
        self.response = V3_response_frame(self.request)

        if seqnums:
            self.seqnums = 0
        else:
            self.seqnums = None

    def run(self):
        while True:
            d = self.s.recvfrom(1024)
            data = d[0]
            addr = d[1]
            self.request.decode(data)
            print ('< ' + self.request.payload.decode('ascii'))
            # discovery response
            if self.request.function == 0:
                self.response.function = self.request.function
                self.response.payload = 'Serial=1234;IP=%s'%addr[0]
                self.response.status = 0
                frame = self.response.encode()
                self.s.sendto(frame , addr)
                print ('  > ' + frame.decode('ascii'))
            else:
                # check password
                if True: #self.requset.pincode == self.password:
                    if self.request.function == 1:
                        self.response.function = self.request.function
                        if self.request.payload == 'boiler.temp':
                            self.response.payload = 'boiler.temp=90'
                            self.response.status = 0
                        elif self.request.payload == 'misc.rsa_key':
                            self.response.payload = 'casyugdyasguyagusduaysgdaysudyasgdyuasdgua'
                            self.response.status = 0
                        frame = self.response.encode()
                        self.s.sendto(frame , addr)
                    else:
                        self.response.function = self.request.function
                        self.response.payload = 'illegal function'
                        self.response.status = 1
                        frame = self.response.encode()
                        self.s.sendto(frame , addr)
                    print ('  > ' + frame.decode('ascii'))
                else:
                    self.response.function = self.request.function
                    self.response.payload = 'wrong password'
                    self.response.status = 1
                    frame = self.response.encode()
                    self.s.sendto(frame , addr)
                    print ('  > ' + frame.decode('ascii'))



