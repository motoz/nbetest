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
from argparse import ArgumentParser
from protocol import Proxy

PORT = 8483 # Controller port
PASSWORD = '0123456789'

def getfunc(args, proxy):
    l = proxy.get(args.path)
    print('\n'.join(l))

def setfunc(args, proxy):
    l = proxy.set(args.path, args.value)
    print('\n'.join(l))

def rawfunc(args, proxy):
    response = proxy.make_request(int(args.function), args.payload)
    if args.verbose:
        print('response from:', proxy.addr)
        print('IP:', proxy.ip, 'Serial', proxy.serial)
        print('received: ' + (response.framedata[1:-1]).decode('ascii'))
        print('   status: %d'%response.status)
        print('   function: %d'%response.function)
        print('   payload:\n      ' + '\n      '.join(response.payload.split(';')))
    else:
        print('\n'.join(response.payload.split(';')))


if __name__ == '__main__':

    argparser = ArgumentParser()
    argparser.add_argument('-v', '--verbose', action='store_true')
    argparser.add_argument('-a', '--address', default=None, help='controller address, autodiscovered if omitted')
    argparser.add_argument('-p', '--password', default=PASSWORD)
    argparser.add_argument('-s', '--serial', default='000000')

    subparsers = argparser.add_subparsers(help='sub-command help')

    # create the parser for the "raw" command
    parser_b = subparsers.add_parser('raw', help='')
    parser_b.add_argument('function', help='')
    parser_b.add_argument('payload', help='')
    parser_b.set_defaults(func=rawfunc)

    # create the parser for the "set" command
    parser_b = subparsers.add_parser('set', help='write item value')
    parser_b.add_argument('path', nargs='?', default = '*', help='path to write')
    parser_b.add_argument('value', nargs='?', help='value to write')
    parser_b.set_defaults(func=setfunc)

    # create the parser for the "get" command
    parser_c = subparsers.add_parser('get', help='get all items')
    parser_c.add_argument('path', nargs='?', default = '*', help='partial of full path to item')
    parser_c.set_defaults(func=getfunc)

    args = argparser.parse_args()

    if args.address is None:
        with Proxy.discover(args.password, PORT, args.serial) as proxy:
            args.func(args, proxy)
    else:
        with Proxy(args.password, PORT, args.address, args.serial) as proxy:
            args.func(args, proxy)





