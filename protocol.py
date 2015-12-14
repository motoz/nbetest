import socket
from random import randrange
import time

START = b'\x02'
END = b'\x04'
RESPONSE_HEADER_SIZE = 10
REQUEST_HEADER_SIZE = 19
STATUS_CODES = (0,1,2,3)
FUNCTION_CODES = (0,1,2,3,4,5,6,7,8,9,10,11)


class Request_frame:
    def __init__(self, function, pin, payload, record=None, sequence_number = 0):
        if sequence_number is not None:
            self.REQUEST_HEADER_SIZE = REQUEST_HEADER_SIZE
        else:
            self.REQUEST_HEADER_SIZE = REQUEST_HEADER_SIZE -2
        if record is None:
            self.framedata = START;
            if function not in FUNCTION_CODES:
                raise IOError
            self.framedata += ('%02u'%function).encode('ascii')
            if len(pin) > 10:
                raise IOError
            if sequence_number is not None:
                self.framedata += ('%02d'%sequence_number).encode('ascii')
            self.framedata += ('%10s'%pin).encode('ascii')
            if len(payload) > 495:
                raise IOError
            self.framedata += ('%03u'%len(payload)).encode('ascii')
            self.framedata += payload.encode('ascii')
            self.framedata += END;
            #print(self.framedata)
        else:
            i = 0
            if not record[i] == START[0]:
                raise IOError
            if len(record) < 17:
                raise IOError
            i += 1
            self.function = int(record[i:i+2])
            i += 2
            if sequence_number is not None:
                self.seqnum = int(record[i:i+2])
                i += 2
            else:
                self.seqnum = None
            self.pin = record[i:i+10].decode('ascii')
            i += 10
            self.size = int(record[i:i+3])
            i += 3
            if not len(record) == self.size + self.REQUEST_HEADER_SIZE:
                raise IOError
            self.payload = record[i:i+self.size]
            i += self.size
            if not record[i] == END[0]:
                raise IOError
    
    @classmethod
    def from_record(cls, record, sequence_number):
        return cls(None, None, None, record, sequence_number)

class Response_frame:
    def __init__(self, function, status, payload, record=None, sequence_number=0):
        if sequence_number is not None:
            self.RESPONSE_HEADER_SIZE = RESPONSE_HEADER_SIZE
        else:
            self.RESPONSE_HEADER_SIZE = RESPONSE_HEADER_SIZE -2
        if record is None:
            self.framedata = START;
            if int(function) > 7:
                raise IOError
            self.framedata += ('%02u'%function).encode('ascii')
            if not status in STATUS_CODES:
                raise IOError
            if sequence_number is not None:
                self.framedata += ('%2d'%sequence_number).encode('ascii')
            self.framedata += ('%1s'%status).encode('ascii')
            if len(payload) > 1007:
                raise IOError
            self.framedata += ('%03u'%len(payload)).encode('ascii')
            self.framedata += payload.encode('ascii')
            self.framedata += END;
        else:
            self.framedata = record
            #print (record)
            i = 0
            if not record[i] == START[0]:
                raise IOError
            if len(record) < self.RESPONSE_HEADER_SIZE:
                raise IOError
            i += 1
            self.function = int(record[i:i+2])
            i += 2
            if sequence_number is not None:
                self.seqnum = int(record[i:i+2])
                i += 2
            else:
                self.seqnum = None
            self.status = int(record[i:i+1])
            i += 1
            self.size = int(record[i:i+3])
            i += 3
            if not len(record) == self.size + self.RESPONSE_HEADER_SIZE:
                raise IOError
            self.payload = (record[i:i+self.size]).decode('ascii')
            i += self.size
            if not record[i] == END[0]:
                raise IOError

    @classmethod
    def from_record(cls, record, sequence_number=0):
        return cls(None, None, None, record, sequence_number)

    def parse_payload(self):
        frame = self.payload
        d = {}
        for item in frame.split(';'):
            name, value = item.split('=')
            d[name] = value
        return d


class Proxy:
    root = ('settings', 'operating_data', 'advanced_data', 'consumption_data', 'event_log','sw_versions','info')
    settings = ('boiler', 'hot_water', 'regulation', 'weather', 'oxygen', 'cleaning', 'hopper', 'fan', 'auger', 'ignition', 'pump', 
        'sun', 'vacuum', 'misc', 'alarm', 'manual', 'bbq_smoke', 'bbq_rotation', 'bbq_grill', 'bbq_meat', 'bbq_afterburner', 'bbq_div')
    consumption_data = ('total_hours', 'total_days', 'total_months', 'total_years', 'dhw_hours', 'dhw_days', 'dhw_months', 'dhw_years')

    def __init__(self, password, port=1900, addr=None, seqnums = True):
        self.password = password
        self.addr = (addr, port)
        if seqnums:
            self.sequence_number = randrange(0,100)
        else:
            self.sequence_number = None
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if addr == '<broadcast>':
            s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.settimeout(0.5)
        self.s = s
        request = Request_frame(0, '0'*10, 'NBE Discovery', sequence_number=self.sequence_number)
        self.s.sendto(request.framedata , (addr, port))
        data, server = self.s.recvfrom(4096)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 0)
        self.addr = server
        response = Response_frame.from_record(data, sequence_number=self.sequence_number).parse_payload()
        if 'Serial' in response:
            self.serial = response['Serial']
        if 'IP' in response:
            self.ip = response['IP']

    def get(self, d=None):
        d = d.rstrip('/').split('/')
        if d[0] is None or d[0] is '*':
            return [p + '/' for p in self.root]
        elif d[0] == 'settings':
            if len(d) == 1:
                return ['settings/%s/'%s for s in self.settings]
            elif d[1] in self.settings:
                if len(d) == 2:
                    response = self.request(1, d[1] + '.*')
                    return ['settings/%s/%s'%(d[1], s) for s in response.payload.split(';')]
                else:
                    response = self.request(1, d[1] + '.' + d[2])
                    try:
                        return (response.payload.split('=')[1],)
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
                response = self.request(f, '*')
                return [d[0] + '/' + s for s in response.payload.split(';')]
            elif len(d) == 2:
                response = self.request(f, d[1])
                try:
                    return (response.payload.split('=')[1],)
                except IndexError:
                    return (response.payload,)
        elif d[0] == 'consumption_data':
            if len(d) == 1:
                return [d[0] + '/' + s for s in self.consumption_data]
            elif d[1] in self.consumption_data:
                response = self.request(6, d[1])
                return [d[0] + '/' + s for s in response.payload.split(';')]
            else:
                return []
        elif d[0] == 'sw_versions':
            if len(d) == 1:
                response = self.request(10, '')
                return [s for s in response.payload.split(';')]
            else:
                return []
        elif d[0] == 'info':
            if len(d) == 1:
                response = self.request(9, '')
                return [s for s in response.payload.split(';')]
            else:
                return []
        elif d[0] == 'event_log':
            if len(d) == 1:
                now = time.strftime('%y%m%d:%H%M%S;',time.localtime())
                response = self.request(8, now)
                return response.payload.split(';')
            else:
                response = self.request(8, d[1])
                return response.payload.split(';')

    def set(self, path=None, value=None):
        d = path.rstrip('/').split('/')
        if d[0] is None or d[0] is '*':
            return ('settings',)
        elif len(d) == 3 and d[1] in self.settings and value is not None :
            response = self.request(2, '.'.join(d[1:3]) + '=' + value)
            if response.status == 0:
                return ('OK',)
            else:
                return (response.payload,)
        else:
            return self.get(path)

    @classmethod
    def discover(cls, password, port, seqnums = True):
        return cls(password, port, addr='<broadcast>', seqnums=seqnums)

    def request(self, function, payload):
        if self.sequence_number is not None:
            self.sequence_number = (self.sequence_number + 1) % 100
        c = Request_frame(int(function), self.password, payload, sequence_number = self.sequence_number)
        #print(' '.join([str(ord(ch)) for ch in c.framedata.decode('ascii')]))
        self.s.sendto(c.framedata , self.addr)
        data, server = self.s.recvfrom(4096)
        response = Response_frame.from_record(data, self.sequence_number)
        #print self.sequence_number, response.seqnum
        if self.sequence_number is not None:
            if response.seqnum == self.sequence_number:
                return response
            else:
                raise IOError
        else:
            return response

class Controller:
    def __init__(self, host, password, port=1900, seqnums=True):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.bind((host, port))
        self.password = password
        if seqnums:
            self.seqnums = 0
        else:
            self.seqnums = None

    def run(self):
        while True:
            d = self.s.recvfrom(1024)
            data = d[0]
            addr = d[1]
            req = Request_frame.from_record(data, sequence_number = self.seqnums)
            print ('< ' + req.payload.decode('ascii'))
            # discovery response
            if req.function == 0:
                res = Response_frame(req.function, 0, 'Serial=1234;IP=%s'%addr[0], sequence_number=req.seqnum)
                self.s.sendto(res.framedata , addr)
                print ('  > ' + res.framedata.decode('ascii'))
            else:
                # check password
                if req.pin == self.password:
                    if req.function == 1:
                        res = Response_frame(req.function, 0, 'boiler.temp=90', sequence_number=req.seqnum)
                        self.s.sendto(res.framedata , addr)
                    else:
                        res = Response_frame(req.function, 1, 'illegal function', sequence_number=req.seqnum)
                        self.s.sendto(res.framedata , addr)
                    print ('  > ' + res.framedata.decode('ascii'))
                else:
                    res = Response_frame(req.function, 1, 'wrong password', sequence_number=req.seqnum)
                    self.s.sendto(res.framedata , addr)
                    print ('  > ' + res.framedata.decode('ascii'))



