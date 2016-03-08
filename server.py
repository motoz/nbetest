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

from argparse import ArgumentParser
from protocol import Controller

HOST = '0.0.0.0'
PORT = 1900
PASSWORD = '0123456789'

if __name__ == '__main__':
    argparser = ArgumentParser()
    argparser.add_argument('-H', '--host', default=HOST, help='default is %s'%HOST)
    argparser.add_argument('-p', '--password', default=PASSWORD)
    argparser.add_argument('-n', '--noseqnum', action='store_true')

    args = argparser.parse_args()

    password = '%10s'%args.password[:10]

    controller = Controller(args.host, password, PORT, not args.noseqnum)
    controller.run()
