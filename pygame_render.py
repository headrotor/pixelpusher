
'''

demoframe:
pygame based frame to display generative color patterns
'''

import pygame
from pygame.locals import *
from pygame.compat import xrange_
import sys
import numpy

import OPC_server




# while(1):
#     opc_server.opc_receive(None,None)



def show (image):

    screen = pygame.display.get_surface()
    screen.fill ((255, 255, 255))
    screen.blit (image, (0, 0))
    pygame.display.flip ()
    while 1:
        event = pygame.event.wait ()
        if event.type == pygame.QUIT:
            raise SystemExit
        if event.type == pygame.MOUSEBUTTONDOWN:
            break


def pygame_handler(chan,pixels):
    """ get a list of pixels from the OPC server and display them"""

    width = 8
    height = 5
    z = 16

    screen = pygame.display.get_surface()
    square=pygame.Surface((z, z))

     # Create the PixelArray.
    ar = pygame.PixelArray(surface)

    for x in range(height):
        for y in range(width):
            index = 3*(x*width + y )
            p = (ord(pixels[index]), 
                 ord(pixels[index + 1]), 
                 ord(pixels[index + 2]))
            #print repr(p)
            square.fill(p)
            draw_me=pygame.Rect((z*x), (z*y), z, z)
     
            screen.blit(square,draw_me)
            pygame.display.flip()       
            #ar[x,y] = p

    #del ar
    #show(surface)




if __name__ == '__main__':
    pygame.init ()

    pygame.display.set_mode((255, 255))
    surface = pygame.Surface((255, 255))

    pygame.display.flip()




    opc_server = OPC_server.OPC_Server(OPC_server.OPC_DEFAULT_PORT,
                                       pygame_handler)

    width = 8
    height = 5

    #pmap = pygame.PixelArray(screen)


    ar = pygame.PixelArray(surface)
    r, g, b = 0, 0, 0
    # Do some easy gradient effect.
    for y in xrange_ (255):
        r, g, b = y, y, y
        ar[:,y] = (r, g, b)
    del ar
    #print "foo"
    #show(surface)

    print "foo"
    while(1):
        print "waiting"
        opc_server.opc_receive(None,None)

