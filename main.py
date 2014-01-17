#!/usr/bin/env python


import time

# local imports

import opc # from github/zestyping
import generative
import numpy as np
import palettes

import scipy.misc.pilutil as smp


numStrings = 1
client = opc.Client('localhost:7890',long_connection = True)

size = (16,16)

ripple = generative.Volterra(size)
#ripple = generative.RippleTest(size)

p = palettes.Palettes()
pals = p.get_all()

pal = pals['hsv']


fn = 'filename.gif'

imdata = np.zeros( (size[0],size[1],3), dtype=np.uint8 )



while(1):
    for n in range(24):

	#client.put_pixels(pixels)
        ripple.iter()
        frame = ripple.get_frame()
        pixels = []
        for i in range(size[0]):
            for j in range(size[1]):
                #print "frame " + repr(frame[i][j])
                #print "pal " + repr(pal[i])
                imdata[i,j] = pal[int(frame[i][j])][0:3]
                pixels.append(pal[int(frame[i][j])][0:3])

        #img = smp.toimage(imdata)
        #img.save('fname%02d.png' % n, 'PNG')
        client.put_pixels(pixels)
        time.sleep(0.1)


