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
import time
import random
from random import SystemRandom

START = b'\x02'
END = b'\x04'
STATUS_CODES = (0,1,2,3)
FUNCTION_CODES = (0,1,2,3,4,5,6,7,8,9,10,11)

class Request_frame(object):
    def __init__(self):
        self.REQUEST_HEADER_SIZE = 52
        self.appid = ''.join([random.choice('abcdefghijk') for a in range(10)])
        self.controllerid = ''.join([random.choice('abcdefghijk') for a in range(10)])
        self.encrypted = False
        self.sequencenumber = 1
        self.pincode = '0123456789'
        self.payload = ''
        self.payloadsize = len(self.payload)
        self.function = 0

    def encode(self):
        while True:
            success = True
            self.framedata = ('%12s'%self.appid[:12]).encode('ascii')
            self.framedata += ('%06d'%int(self.controllerid[:6])).encode('ascii')

            if self.encrypted:
                if hasattr(self, 'xtea_key'):
                    #print ('xtea encrypt 1')
                    self.framedata += ('%1s'%'-').encode('ascii')
                else:
                    self.framedata += ('%1s'%'*').encode('ascii')
            else:
                self.framedata += ('%1s'%' ').encode('ascii')

            h = START;
            if self.function not in FUNCTION_CODES:
                raise IOError
            h += ('%02u'%self.function).encode('ascii')
            h += ('%02d'%self.sequencenumber).encode('ascii')

            if self.encrypted:
                h += ('%10s'%self.pincode[:10]).encode('ascii')
            else:
                h += '0000000000'.encode('ascii')

            h += ('%10s'%int(time.time())).encode('ascii')
            h += ('%4s'%'pad ').encode('ascii')
            h += ('%03u'%len(self.payload)).encode('ascii')
            if len(self.payload) > 495:
                raise IOError
            try:
                h += self.payload.encode('ascii')
            except UnicodeError:
                h += self.payload
            h += END;
            if self.encrypted: 
                pad = b''.join([bytes(chr(SystemRandom().randrange(128)), 'utf-8') for x in range(64-len(h))])
                h+=pad
                if hasattr(self, 'xtea_key'):
                    #print ('xtea encrypt 2')
                    h = self.xtea_key.encrypt(h)
                else:
                    h = self.public_key.encrypt(h, None)[0]
                    if len(h) != 64:
                        success = False
            self.framedata += h
            if success:
                return self.framedata
            print ('ERROR chipertext wrong length', len(h))

    def decode(self, record):
        i = 0
        self.appid = record[i:12]
        i+=12
        self.controllerid = record[i:6]
        i+=6
        self.encryption = record[i:1]
        i+=1
        if not record[i] == START[0]:
            raise IOError
        if len(record) < 17:
            raise IOError
        i += 1
        self.function = int(record[i:i+2])
        i += 2
        self.sequencenumber = int(record[i:i+2])
        i += 2
        self.pincode = record[i:i+10].decode('ascii')
        i += 10
        self.timestamp = int(record[i:i+10].decode('ascii'))
        i += 10
        self.extra = record[i:i+4].decode('ascii')
        i += 4
        self.payloadsize = int(record[i:i+3])
        i += 3
        if len(record) < self.payloadsize + self.REQUEST_HEADER_SIZE:
            raise IOError
        self.payload = record[i:i+self.payloadsize]
        i += self.payloadsize
        if not record[i] == END[0]:
            raise IOError

class Response_frame(object):
    def __init__(self, request):
        self.RESPONSE_HEADER_SIZE = 28
        self.request = request

    def encode(self):
        self.framedata = ('%12s'%self.request.appid).encode('ascii')
        self.framedata += ('%6s'%self.request.controllerid).encode('ascii')
        self.framedata += START;
        if int(self.function) > 13:
            raise IOError
        self.framedata += ('%02u'%self.function).encode('ascii')
        if self.status not in STATUS_CODES:
            raise IOError
        self.framedata += ('%2d'%self.request.sequencenumber).encode('ascii')
        self.framedata += ('%1s'%self.status).encode('ascii')
        if len(self.payload) > 1007:
            raise IOError
        self.framedata += ('%03u'%len(self.payload)).encode('ascii')
        self.framedata += self.payload.encode('ascii')
        self.framedata += END;
        return self.framedata

    def decode(self, record):
        self.framedata = record
        i = 0
        self.appid = record[i:i+12]
        i+=12
        self.controllerid = record[i:i+6]
        i+=6
        #import pdb;pdb.set_trace()i
        if not record[i] == START[0]:
            raise IOError
        if len(record) < self.RESPONSE_HEADER_SIZE:
            raise IOError
        i += 1
        self.function = int(record[i:i+2])
        i += 2
        self.sequencenumber = int(record[i:i+2])
        if self.sequencenumber != self.request.sequencenumber:
        #    print (self.sequencenumber, self.request.sequencenumber)
            raise IOError
        i += 2
        self.status = int(record[i:i+1])
        i += 1
        self.size = int(record[i:i+3])
        i += 3
        if not len(record) == self.size + self.RESPONSE_HEADER_SIZE:
            raise IOError
        #print (record[i:i+self.size])
        self.payload = (record[i:i+self.size]).decode('ascii')
        #print (self.payload)
        i += self.size
        if not record[i] == END[0]:
            raise IOError

    def parse_payload(self):
        frame = self.payload
        d = {}
        for item in frame.split(';'):
            name, value = item.split('=')
            d[name] = value
        return d

