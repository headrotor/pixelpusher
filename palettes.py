#!/usr/bin/python
import random
import sys
import math
import numpy as np
import colorsys
import random
import os
import PIL


try:
    MATPLOT_OK = True
    import matplotlib.pyplot as plt
    import matplotlib.colors
except ImportError:
    MATPLOT_OK = False

# Todo: use L*a*b colorspace from 

class Palettes():
    """ Class to generate color palettes for LED patterns or what have you"""

    def __init__(self,length=256):
        self.qual_names = ['Accent', 'Dark2', 'hsv', 'Paired', 'Pastel1',
                             'Pastel2', 'Set1', 'Set2', 'Set3', 'spectral']

        self.length = length    # standard number of colors in palette
        self.height = int(length/8)  # height of palette for output image

    def get_all(self):
        """ generate all palettes and return in a dict"""
        pals = {}
        if MATPLOT_OK:
            pals['grayscale'] = self.grayscale()

            for name in self.qual_names:
                pals[name] = self.get_matplot_cmap(name)

        # test for existence of pallette directory
        #self.get_all_cmaps("./palettes/",pals)

        return pals

    def flame(self):
        """ Make a flamey palette that goes yellow -> red -> black
        Shamelessly pilfered from http://www.pygame.org/pcr/numpy_flames/"""
        gstep, bstep = 75, 150
        cmap = np.zeros((256, 3))
        cmap[:, 0] = np.minimum(np.arange(256) * 3, 255)
        cmap[gstep:, 1] = cmap[:-gstep, 0]
        cmap[bstep:, 2] = cmap[:-bstep, 0]
        return cmap  

    def get_matplot_cmap(self,cmap_name):
        cmap=plt.get_cmap(cmap_name)
        cmap = cmap(range(256))
        #print repr(cmap)
        sys.stdout.flush()
        return(255*cmap)


    def grayscale(self):
        """grayscale """
        segmentdata = { 'red': [(0.0, 0.0, 0.0),
                                (1.0, 255.0, 255.0)],
                        'green': [(0.0, 0.0, 0.0),
                                (1.0, 255.0, 255.0)],
                        'blue': [(0.0, 0.0, 0.0),
                                (1.0, 255.0, 255.0)]}


        cmap = matplotlib.colors.LinearSegmentedColormap('foo',segmentdata)
        return [ cmap(1.*i/256) for i in range(256)]


    def get_all_cmaps(self,imgdir,cmap_list): 
        """ make a palette from every png file in this directory"""
        for f in os.listdir(imgdir):
            fname = os.path.join(imgdir, f)
            print fname
            if os.path.isfile(fname):
                base, ext = os.path.splitext(os.path.basename(fname))
          #base = os.path.basename(fname)
                print " b: %s e: %s" % (base, ext)
                if ext.lower() == '.png':
                    cmap_list[base] = self.get_cmap_image(fname)
                    print "loading colormap from %s" % fname


    def export_palette(self,pal,name='exported_palette.png'):
        """ Given a palette, export it as a png. """
        import scipy.misc.pilutil as smp
        import PIL
        width = len(pal)
        height = self.height
        # make output image data array
        imdata = np.zeros( (height,width,3), dtype=np.uint8 )
        # fill with palette data
        for i in range(width):
            for j in range(height):
                #print "frame " + repr(frame[i][j])
                #print "pal " + repr(pal[i])
                imdata[j,i] = pal[i][0:3]

        img = smp.toimage(imdata)
        img.save(name, 'PNG')

    def palette_from_hsv(self,h,s,v,wobble=0.0):
        """ calculate a rgb palette from the given hsv color"""
        cmap = np.zeros((self.length, 3))
        rgb = self.uint8_to_float([h,s,v])
        # line through through HSV space
        h_noise = self.smoothed_noise(self.length)
        s_noise = self.smoothed_noise(self.length)
        # should maybe detrend noise arrays but can't be bothered
        for i in range(self.length):
            rh = h
            rs = s
            if wobble > 0:
                # give hue a random offset
                rh += wobble*(h_noise[i])
                if rh < 0.0:
                    rh += 1.0
                elif rh > 1.0:
                    rh -= 1.0

                # give saturation a random offset
                rs += wobble*(s_noise[i])/2.0
                if rs < 0.0:
                    rs  = 0.0
                elif rs > 1.0:
                    rs = 1.0
            rgb = colorsys.hsv_to_rgb(rh, rs, float(i/255.0))
            print repr(rs)
            cmap[i, 0] = 255*rgb[0]
            cmap[i, 1] = 255*rgb[1]
            cmap[i, 2] = 255*rgb[2]
            #cmap[i, 0] = 255*(noise[i] + 0.5)
            #cmap[i, 1] = 255*(noise[i] + 0.5)
            #cmap[i, 2] = 255*(noise[i] + 0.5)
        
        return cmap

    def palette_from_rgb(self,rgb_ints):
        cmap = np.zeros((self.length, 3))
        rgb = self.uint8_to_float(rgb_ints)
        cmap[:, 0] = rgb[0]*np.arange(256)
        cmap[:, 1] = rgb[1]*np.arange(256)
        cmap[:, 2] = rgb[2]*np.arange(256)
        print repr(cmap[:,0])
        return cmap


    def uint8_to_float(self,listofints):
        return [ float(int(l)/255.0) for l in listofints]
 
    
    def float_to_uint8(self,listoffloats):
        return [ int(math.floor(0.5 + l*255)) for l in listoffloats]
        
    def smoothed_noise(self,length=None):
        """ return an array of smoothed random noise"""
        if length is None: length = self.length
        noise_arr = np.random.random(length) - 0.5
        return self.smooth(noise_arr)

    def smooth(self,x,window_len=15,window='hanning'):
        """smooth a data array using a window with requested size. 
        from http://wiki.scipy.org/Cookbook/SignalSmooth """
        if x.ndim != 1:
            raise ValueError, "smooth only accepts 1 dimension arrays."

        if x.size < window_len:
            raise ValueError, "Input vector needs to be bigger than window size."
        if window_len<3:
            return x

        if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
            raise ValueError, "Window is one of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'"


        s=np.r_[x[window_len-1:0:-1],x,x[-1:-window_len:-1]]
        #print(len(s))
        if window == 'flat': #moving average
            w=np.ones(window_len,'d')
        else:
            w=eval('np.'+window+'(window_len)')

        y=np.convolve(w/w.sum(),s,mode='valid')
        return y


usage = """Usage: palettes.py [op] [color] [arg]
[op]  -- operation, one of:
         rgb -- make palette from rgb color
         hsv -- make palette from HSV color
         
[color] -- comma-separated color triple (no spaces) 


"""


# todo: read ggr files? http://nedbatchelder.com/code/modules/ggr.html
             
if __name__ == "__main__":
    """ Excercise the Palettes class from the command line """

    if len(sys.argv) < 2:
        print usage
        exit()

    pal = Palettes()
    

    pals = pal.get_all()


    op = sys.argv[1]

    if op.lower() == 'rgb':
        print "generating palette from rgb values"
        rgb_str = sys.argv[2].split(',')
        print repr(pal.uint8_to_float(rgb_str))
        newpal = pal.palette_from_rgb(rgb_str)
        pal.export_palette(newpal)

    elif op.lower() == 'hsv':
        print "generating palette from rgb values"
        rgb = pal.uint8_to_float(sys.argv[2].split(','))
        h = colorsys.rgb_to_hsv(rgb[0],rgb[1],rgb[2])
        #print repr(pal.uint8_to_float(rgb_str))
        newpal = pal.palette_from_hsv(h[0],h[1],h[2],wobble=0.5)
        pal.export_palette(newpal)
