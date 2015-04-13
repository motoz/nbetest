import socket

START = '\x02'
END = '\x04'
RESPONSE_HEADER_SIZE = 8
REQUEST_HEADER_SIZE = 17
STATUS_CODES = (0,1,2,3)
FUNCTION_CODES = (0,1,2,3,4,5,6,7,10)


class Request_frame:
    def __init__(self, function, pin, payload, record=None):
        if record is None:
            self.framedata = START;
            if function not in FUNCTION_CODES:
                raise IOError
            self.framedata += '%02u'%function
            if len(pin) > 10:
                raise IOError
            self.framedata += '%10s'%pin
            if len(payload) > 495:
                raise IOError
            self.framedata += '%03u'%len(payload)
            self.framedata += payload
            self.framedata += END;
        else:
            i = 0
            if not record[i] == START:
                raise IOError
            if len(record) < 17:
                raise IOError
            i += 1
            self.function = int(record[i:i+2])
            i += 2
            self.pin = record[i:i+10]
            i += 10
            self.size = int(record[i:i+3])
            i += 3
            if not len(record) == self.size + REQUEST_HEADER_SIZE:
                raise IOError
            self.payload = record[i:i+self.size]
            i += self.size
            if not record[i] == END:
                raise IOError
    
    @classmethod
    def from_record(cls, record):
        return cls(None, None, None, record)

class Response_frame:
    def __init__(self, function, status, payload, record=None):
        if record is None:
            self.framedata = START;
            if int(function) > 7:
                raise IOError
            self.framedata += '%02u'%function
            if not status in STATUS_CODES:
                raise IOError
            self.framedata += '%1s'%status
            if len(payload) > 1007:
                raise IOError
            self.framedata += '%03u'%len(payload)
            self.framedata += payload
            self.framedata += END;
        else:
            self.framedata = record
            i = 0
            if not record[i] == START:
                raise IOError
            if len(record) < RESPONSE_HEADER_SIZE:
                raise IOError
            i += 1
            self.function = record[i:i+2]
            i += 2
            self.status = record[i:i+1]
            i += 1
            self.size = int(record[i:i+3])
            i += 3
            if not len(record) == self.size + RESPONSE_HEADER_SIZE:
                raise IOError
            self.payload = record[i:i+self.size]
            i += self.size
            if not record[i] == END:
                raise IOError

    @classmethod
    def from_record(cls, record):
        return cls(None, None, None, record)

def parse_response(frame):
    d = {}
    for item in frame.split(';'):
        name, value = item.split('=')
        d[name] = value
    return d

class Proxy:
    def __init__(self, password, port=1900, addr=None):
        self.password = password
        self.addr = (addr, port)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.settimeout(0.5)
        self.s = s
        request = Request_frame(0, '0'*10, 'NBE Discovery')
        self.s.sendto(request.framedata , (addr, port))
        data, server = self.s.recvfrom(4096)
        self.addr = server
        response = parse_response(Response_frame.from_record(data).payload)
        if 'Serial' in response:
            self.serial = response['Serial']
        if 'IP' in response:
            self.ip = response['IP']

    @classmethod
    def discover(cls, password):
        return cls(password, addr='<broadcast>')

    def request(self, function, payload):
        c = Request_frame(int(function), self.password, payload)
        self.s.sendto(c.framedata , self.addr)
        data, server = self.s.recvfrom(4096)
        return Response_frame.from_record(data)
    
    def menu(self, menu):
        menus = ('boiler', 'hot_water', 'regulation')
        res = self.request(1, 'boiler.*')

class Controller:
    def __init__(self, host, password, port=1900):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.bind((host, port))
        self.password = password

    def run(self):
        while True:
            d = self.s.recvfrom(1024)
            data = d[0]
            addr = d[1]
            req = Request_frame.from_record(data)

            # discovery response
            if req.function == 0:
                res = Response_frame(req.function, 0, 'Serial=1234;IP=%s'%addr[0])
                self.s.sendto(res.framedata , addr)
            else:
                # check password
                if req.pin == self.password:
                    if req.function == 1:
                        res = Response_frame(req.function, 0, 'boiler.temp=90')
                        self.s.sendto(res.framedata , addr)
                    else:
                        res = Response_frame(req.function, 1, 'illegal function')
                        self.s.sendto(res.framedata , addr)
                else:
                    res = Response_frame(req.function, 1, 'wrong password')
                    self.s.sendto(res.framedata , addr)



