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

