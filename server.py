from argparse import ArgumentParser
from protocol import Controller

HOST = '0.0.0.0'
PORT = 1900
PASSWORD = '0123456789'

if __name__ == '__main__':
    argparser = ArgumentParser()
    argparser.add_argument('-H', '--host', default=HOST, help='default is %s'%HOST)
    argparser.add_argument('-p', '--password', default=PASSWORD)

    args = argparser.parse_args()

    password = '%10s'%args.password[:10]

    controller = Controller(args.host, args.password, PORT)
    controller.run()
