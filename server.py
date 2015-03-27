import socket
import sys
from argparse import ArgumentParser
import protocol

HOST = '0.0.0.0'
PORT = 1900
PASSWORD = '0123456789'

if __name__ == '__main__':
    argparser = ArgumentParser()
    argparser.add_argument('-s', '--silent', action='store_true')
    argparser.add_argument('-H', '--host', default=HOST, help='default is %s'%HOST)
    argparser.add_argument('-p', '--password', default=PASSWORD)

    args = argparser.parse_args()

    password = '%10s'%args.password

    try :
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        if not args.silent:
            print 'Socket created'
    except socket.error, msg :
        print 'Failed to create socket. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
        sys.exit()

    try:
        s.bind((args.host, PORT))
    except socket.error , msg:
        print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
        sys.exit()

    while True:
        # receive data from client (data, addr)
        d = s.recvfrom(1024)
        data = d[0]
        addr = d[1]

        if not data: 
            print 'no data'
            break

        req = protocol.Request_frame.from_record(data)

        if not args.silent:
            print 'addr: ', addr
            print 'password: ' + req.pin
            print 'function: ' + str(req.function)
            print 'payload: '  + req.payload

        # discovery response
        if req.function == 0:
            res = protocol.Response_frame(req.function, 0, 'Serial=1234;IP=%s'%addr[0])
            s.sendto(res.framedata , addr)
        else:
            # check password
            if req.pin == password:
                if req.function == 1:
                    res = protocol.Response_frame(req.function, 0, 'boiler.temp=90')
                    s.sendto(res.framedata , addr)
                else:
                    res = protocol.Response_frame(req.function, 1, 'illegal function')
                    s.sendto(res.framedata , addr)
            else:
                res = protocol.Response_frame(req.function, 1, 'wrong password')
                s.sendto(res.framedata , addr)
                if not args.silent:
                    print 'wrong pin: %s'%req.pin

    s.close()
