__author__  = 'Xose Perez'
__email__   = 'xose.perez@gmail.com'
__license__ = 'TBD'

import binascii

MESSAGES = [
   # '7e001017000013a20040401122fffe0244320407',
   # '7e001017000013a20040401122fffe0244330406',
     '7e0015900013a200404011220123405354415455533a310a4a',
]

class Serial(object):

    stream = None
    length = 0
    index = 0

    def __init__(self, *args, **kwargs):
        self.stream = binascii.unhexlify(''.join(MESSAGES))
        self.length = len(self.stream)

    def inWaiting(self):
        return self.length - self.index

    def read(self):
        response = None
        if self.inWaiting() > 0:
            response = self.stream[self.index]
            self.index += 1
        return response

    def write(self, message):
        print binascii.hexlify(message)

    def close(self):
        None
