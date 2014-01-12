#!/usr/bin/env python

"""Python Server library for Open Pixel Control
http://github.com/zestyping/openpixelcontrol

Gets pixel values from an OPC client to be displayed.
http://openpixelcontrol.org/

By Jonathan Foote rotormind.com January 2014
"""

import sys
import socket
import select
import struct

# class source(object):

# typedef struct {
#   u16 port;
#   int listen_sock;
#   int sock;
#   u16 header_length;
#   u8 header[4];
#   u16 payload_length;
#   u8 payload[1 << 16];
# } opc_source_info;



OPC_DEFAULT_PORT = 7890
OPC_SET_PIXELS = 0x00


class OPC_source_info(object):
    """holds info for Open Pixel Control socket connection"""
    def __init__(self, server_port, handler):    
        self._port = server_port
        self.sock = None
        self.OPC_DEFAULT_PORT = 7890
        self.handler = handler
        self.reset()
        

    def reset(self):
        self.payload = []
        self.payload_expected = 0
        self.chan = None
        self.cmd = None
        self.conn = None
        self.header = ''

        if self.sock is None:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #self.sock.setblocking(0)
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind(('localhost', self._port))
            self.sock.listen(1)

    def parse_header(self):
        assert len(self.header) == 4 
        self.chan, self.cmd, length = struct.unpack('!BBH',self.header)
        self.payload_expected = int(length)

    def payload_complete(self):
        if len(self.header) < 4:
            return False
        if self.payload_expected == len(self.payload):
            return True
        return False

    def do_handler(self):
        if self.handler is not None:
            self.handler(self.chan, self.payload)

class OPC_Server(object):

    def __init__(self, server_port, handler,verbose = False):
        """Create an OPC client object which sends pixels to an OPC server.

        server_ip_port should be an ip:port or hostname:port as a single string.
        For example: '127.0.0.1:7890' or 'localhost:7890'
        """

        self.verbose = verbose

        self.info = OPC_source_info(server_port,handler)

    def opc_receive(self,handler,timeout=1.0):


        # you can add additional sockets to this list
        input_list = [self.info.sock]

        sys.stdout.flush()
        inready,outready,exready = select.select(input_list,[],[],timeout)

        if len(inready) == 0:
            # we timed out, return false if anyone cares 
            # print "timeout"
            return False

        for s in inready:

            if s == self.info.sock:
                # data on the socket, handle it:
                if self.info.conn is not None:
                    # continue reading from open connection
                    print "still reading"
                else:           # new connection, open it...
                    self.info.conn, addr = self.info.sock.accept()
                    print 'OPC: Client connected from ' +  repr(addr)
                    #  get header if we haven't yet

                if len(self.info.header) < 4:
                    self.info.header += self.info.conn.recv(
                        4 - len(self.info.header))
                    if len(self.info.header) == 4:
                        self.info.parse_header()
                        print "got header"

                if not self.info.payload_complete():
                    print "reading payload %d " % len(self.info.payload)
                    self.info.payload += self.info.conn.recv(
                        self.info.payload_expected - len(self.info.payload))

                if self.info.payload_complete():
                    print "payload complete " 
                    if self.info.cmd == OPC_SET_PIXELS:
                        self.info.do_handler()
                    self.info.reset()

        return True


    def _debug(self, m):
        if self.verbose:
            print '    %s' % str(m)


    def handle_pixels(self, pixels, channel=0):
        """Send the list of pixel colors to the OPC server on the given channel.

        channel: Which strand of lights to send the pixel colors to.
            Must be an int in the range 0-255 inclusive.
            0 is a special value which means "all channels".

        pixels: A list of 3-tuples representing rgb colors.
            Each value in the tuple should be in the range 0-255 inclusive. 
            For example: [(255, 255, 255), (0, 0, 0), (127, 0, 0)]
            Floats will be rounded down to integers.
            Values outside the legal range will be clamped.

        Will establish a connection to the server as needed.

        On successful transmission of pixels, return True.
        On failure (bad connection), return False.

        The list of pixel colors will be applied to the LED string starting
        with the first LED.  It's not possible to send a color just to one
        LED at a time (unless it's the first one).

        """
        pass

    def parse_OPC(message):
        pixels = message
        # parse OPC message
        len_hi_byte = int(len(pixels)*3 / 256)
        len_lo_byte = (len(pixels)*3) % 256
        header = chr(channel) + chr(0) + chr(len_hi_byte) + chr(len_lo_byte)
        pieces = [header]
        for r, g, b in pixels:
            r = min(255, max(0, int(r)))
            g = min(255, max(0, int(g)))
            b = min(255, max(0, int(b)))
            pieces.append(chr(r) + chr(g) + chr(b))
        message = ''.join(pieces)

def test_handler(channel, pixels):
    """ demonstratin  pixel handler function, called when a OPC packet is
    received. pixels is a list of 8-bit pixel data"""

    print "got packet, channel %d" % channel
    if len(pixels) > 10:
        pixels = pixels[1:10]
    print ' '.join(["%02x" % ord(p) for p in pixels])
                   
               


if __name__ == '__main__': 

    opc_server = OPC_Server(OPC_DEFAULT_PORT,test_handler)
    
    while(1):
        opc_server.opc_receive(None,None)



