import socket
import sys
from argparse import ArgumentParser
import protocol


PORT = 1900 # Controller port
PASSWORD = '0123456789'

class Controller:
    def __init__(self, port=1900, addr=None):
        self.addr = (addr, port)

    @classmethod
    def discover(cls):
        try :
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)        
            s.settimeout(0.5)
        except socket.error, msg :
            print 'Failed to create socket. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
        try:
            c = protocol.Request_frame(0, '0'*10, 'NBE Discovery')
            s.sendto(c.framedata , ('<broadcast>', PORT))
            data, server = s.recvfrom(4096)
            response = protocol.Response_frame.from_record(data)
            if args.verbose:
                print 'discovery:'
                print 'send:     ' + c.framedata[1:-1]
                print 'received: ' + response.framedata[1:-1]
                print 'status: ' + response.status
                print 'function: ' + response.function
                print 'payload: ' + '\n'.join(response.payload.split(';'))
        except IOError:
            print 'server discovery failed'
            sys.exit()
        return cls(addr=server[0])

if __name__ == '__main__':

    argparser = ArgumentParser()
    argparser.add_argument('-v', '--verbose', action='store_true')
    argparser.add_argument('-a', '--address', default=None, help='controller address, autodiscovered if omitted')
    argparser.add_argument('-p', '--password', default=PASSWORD)
    argparser.add_argument('function')
    argparser.add_argument('payload')

    args = argparser.parse_args()

    try :
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.settimeout(1)
    except socket.error, msg :
        print 'Failed to create socket. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
        sys.exit()

    if args.address is None:
        controller = Controller.discover()
    else:
        controller = Controller(PORT, args.address)

    c = protocol.Request_frame(int(args.function), args.password, args.payload)

    try:
        s.sendto(c.framedata , controller.addr)
        data, server = s.recvfrom(4096)
        response = protocol.Response_frame.from_record(data)

        if args.verbose:
            print 'response:'
            print 'send:     ' + c.framedata[1:-1]
            print 'received: ' + response.framedata[1:-1]
            print 'status: ' + response.status
            print 'function: ' + response.function
            print 'payload: ' + '\n'.join(response.payload.split(';'))
        else:
            print '\n'.join(response.payload.split(';'))

    except socket.error, msg :
        print 'Socket error: ' + str(msg)

