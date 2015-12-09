from __future__ import print_function
from argparse import ArgumentParser
from protocol import Proxy

PORT = 1900 # Controller port
PASSWORD = '0123456789'


if __name__ == '__main__':

    argparser = ArgumentParser()
    argparser.add_argument('-v', '--verbose', action='store_true')
    argparser.add_argument('-a', '--address', default=None, help='controller address, autodiscovered if omitted')
    argparser.add_argument('-p', '--password', default=PASSWORD)
    argparser.add_argument('-n', '--noseqnum', action='store_true')
    argparser.add_argument('function')
    argparser.add_argument('payload')

    args = argparser.parse_args()

    if args.address is None:
        proxy = Proxy.discover(args.password, PORT, seqnums = not args.noseqnum)
    else:
        proxy = Proxy(args.password, PORT, args.address, not args.noseqnum)

    response = proxy.request(args.function, args.payload)

    if args.verbose:
        print('response from:', proxy.addr)
        print('IP:', proxy.ip, 'Serial', proxy.serial)
        print('received: ' + (response.framedata[1:-1]).decode('ascii'))
        print('   status: %d'%response.status)
        print('   function: %d'%response.function)
        print('   payload:\n      ' + '\n      '.join(response.payload.split(';')))
    else:
        print('\n'.join(response.payload.split(';')))

