#!/usr/bin/python
import random
import sys
import numpy as np
import colorsys
import os
import PIL


try:
    MATPLOT_OK = True
    import matplotlib.pyplot as plt
    import matplotlib.colors
except ImportError:
    MATPLOT_OK = False


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
        cmap = numpy.zeros((256, 3))
        cmap[:, 0] = numpy.minimum(numpy.arange(256) * 3, 255)
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


usage = """Usage: palettes.py [op] [color] [arg]
[op]  -- operation, one of:
         rgb -- make palette from rgb color
         hsv -- make palette from HSV color
         
[color] -- color triple in form that can be parsed 


"""

if __name__ == "__main__":
    """ Excercise the Palettes class from the command line """

    if len(sys.argv) < 2:
        print usage
        exit()

    pal = Palettes()
    

    pals = pal.get_all()

    pal.export_palette(pals['hsv'])

    op = sys.argv[1]
    if op.lower() == 'rgb':
        print "generating palette from rgb values"
