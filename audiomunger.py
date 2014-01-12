#!/usr/bin/python
# -*- coding: utf-8 -*-


""" audiomunger: extract spectral features from audio input"""

import thread
import time

import pyaudio
import sys
from numpy import *
from numpy.fft import *
from struct import *
import traceback

chunk = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 22500
RECORD_SECONDS = 5


# ----------------------------------------------------------------------

# This creates a new Event class and a EVT binder function

class AudioSampler:

    def __init__(self, callback, nbands=8):

        self.callback = callback
        p = pyaudio.PyAudio()
        self.p = p
        self.stream = p.open(format=FORMAT, channels=CHANNELS,
                             rate=RATE, input=True, output=True)

        print "AudioProc init: recording"

        csum = []
        spectlen = RATE / chunk * RECORD_SECONDS
        self.makebands(chunk / 2)
        self.bmax = 0
        self.gain = 1.0
        self.skip = 8  # skip this many windows

    def setgain(self, intgain):
        self.gain = 2 * intgain / 100.0

        print "AudioProc gain is " + str(self.gain)
        sys.stdout.flush()

    def makebands(self, max):
        '''make a set of power-of-two bands. Max must be power of 2'''

        self.bands = []
        self.scale = []
        while max > 2:

#            print "start : %4d stop: %4d" % (max/2, max)

            self.bands.append(range(max / 2, max))
            self.scale.append(max)
            max = max / 2
        self.bands[-1] = range(0, 4)

        # reverse the bands from low to high

        self.bands.reverse()
        self.scale.reverse()

    def Start(self):
        self.keepGoing = self.running = True
        try:
            thread.start_new_thread(self.Run, ())
        except Exception: # catch exception, 
            traceback.print_exc()


    def Stop(self):

#        print "got stop command"

        sys.stdout.flush()
        self.keepGoing = False

    def Restart(self):

#        print "got restart command"

        sys.stdout.flush()
        self.keepGoing = True

    def Run(self):
        i = 0
        while self.keepGoing:
            i += 1
            data = self.stream.read(chunk)
            if i > 2:

#            if (i>self.skip):

                i = 0

            # print unpack('B',data[0])

                buff = array(unpack_from('1024h', data))

                # e = buff.std()
                # print "Energy: %f" % e
                # sys.stdout.flush()
             # # use stdev to calculate energy in this buffer (root sum of squared mag)
            # csum.append(buff.std())

                fourier = fft(buff)

            # # calculate log mag of fft

                logmag = hypot(fourier.real[0:chunk / 2],
                               fourier.imag[0:chunk / 2])
                if False:
                    self.lmfile = open('logmag.txt', 'w')
                    logmag.tofile(self.lmfile, sep=' ', format='%s')
                    self.lmfile.close()
                bdata = []

#                i = 0

                for (i, b) in enumerate(self.bands):

                    # sum energy in this band

                    bdata.append(logmag[b].mean() * self.scale[i])

#                    i += 1

                    # normalize so max energy is 1.0

                localmax = []
                localmax.append(max(bdata))
                localmax.append(self.bmax)
                self.bmax = max(localmax)
                for i in range(len(bdata)):
                    bdata[i] = bdata[i] * self.gain / self.bmax

                try:
                    self.callback(self.client, bdata)
                except Exception: # catch exception, 
                    traceback.print_exc()

                # print localmax[0]

                if True:
                    time.sleep(0.01)

                # self.bwfile=open("bands.txt","w")
                # self.bwfile.write(str(bdata))
                # self.bwfile.close()

                # bands = logmag[0:chunk/4]
                # nbands = 16
                # bwidth = chunk/(4*nbands)
                # bsum = mean(bands.reshape(nbands,bwidth),axis=1)
            # line.set_ydata(logmag)

            # # convert to 2d array and append to running show.
            # logmag2 = array(logmag.tolist(),ndmin=2)

        self.running = False

    def close(self):
        print 'closing audio device'
        sys.stdout.flush()
        self.Stop()
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()



import opc # from github/zestyping

import numpy as np
import scipy.misc.pilutil as smp


def sample_callback(client,data):
    size = (5, 8)
    #imdata = np.zeros( (size[0],size[1],3), dtype=np.uint8 )

        
    pixels = []
    sys.stdout.flush()
    #return
    for i in range(size[0]):
        for j in range(size[1]):
            #print "frame " + repr(frame[i][j])
            #print "pal " + repr(pal[i])
            pix = int(256 * data[j])
            if pix > 255:
                pix = 255
            #if i == 0:
            #    print repr(pix)
            pixels.append((pix,pix,pix))
            #pixels.append(pix)
            #pixels.append(pix)
        sys.stdout.flush()
    client.put_pixels(pixels)
        
        

if __name__ == '__main__':
    audio_in = AudioSampler(sample_callback)
    audio_in.client = opc.Client('localhost:7890')
    audio_in.Start()
    while(1):
        print "waiting"
        time.sleep(1)





