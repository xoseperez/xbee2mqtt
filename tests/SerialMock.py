import binascii

# Some sample messages
#   '17000013a20040401122fffe02443204',                            # Remote AT request: ATD24
#   '900013a20040401122012340' + binascii.hexlify('status:1\n'),   # Receive well-formed serial packet
#   '900013a20040401122012340' + binascii.hexlify('abcdefgh\n'),   # Receive random serial packet
#   '920013a2004040112201230101100384100201000081',                # IO Sample DIO0:0, DIO1:1, DIO12:1, ADC2:256 ADC7(Supply Voltage):129
#   '920013a200406bfd090123010110008010000B00',                    # IO Sample DIO12:1, ADC7(Supply Voltage):2816

class Serial(object):

    stream = ''
    length = 0
    index = 0

    data = ''

    def _split_len(self, seq, length):
            return [seq[i:i+length] for i in range(0, len(seq), length)]

    def __init__(self, port, baudrate):
        pass

    def feed(self, message):
        bytes = self._split_len(message,2)
        checksum = 0xFF - (sum([int(x,16) for x in bytes]) & 0xFF)
        message = '7e' + "%04x" % len(bytes) + message + "%02x" % checksum
        message = binascii.unhexlify(message)
        self.stream += message
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
        self.data += message

    def close(self):
        None
