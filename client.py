from argparse import ArgumentParser
from protocol import Proxy


PORT = 1900 # Controller port
PASSWORD = '0123456789'


if __name__ == '__main__':

    argparser = ArgumentParser()
    argparser.add_argument('-v', '--verbose', action='store_true')
    argparser.add_argument('-a', '--address', default=None, help='controller address, autodiscovered if omitted')
    argparser.add_argument('-p', '--password', default=PASSWORD)
    argparser.add_argument('function')
    argparser.add_argument('payload')

    args = argparser.parse_args()

    if args.address is None:
        proxy = Proxy.discover(args.password)
    else:
        proxy = Proxy(args.password, PORT, args.address)

    response = proxy.request(args.function, args.payload)

    if args.verbose:
        print 'response from:', proxy.addr
        print 'IP:', proxy.ip, 'Serial', proxy.serial
        print 'received: ' + response.framedata[1:-1]
        print '   status: ' + response.status
        print '   function: ' + response.function
        print '   payload:\n      ' + '\n      '.join(response.payload.split(';'))
    else:
        print '\n'.join(response.payload.split(';'))

