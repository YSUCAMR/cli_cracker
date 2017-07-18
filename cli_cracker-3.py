from collections import deque
import sys
import struct
import numpy as np
import time
from matplotlib import pyplot as plt
import datetime
import re
import cv2
import math
import datetime
import itertools

def cli_readerbinary( fileinput ):

    l = []
    l1 = []
    poly_lines = []
    directions = []
    layers = []
    layer_directions = []
    ASCII = True
    Binary = False

    dq1 = deque(['.','.','H','E','A','D','E','R','E','N','D'])
    dq2 = deque(['$','$','H','E','A','D','E','R','E','N','D'])

    scale = 0.5
    bytes_read = open(fileinput, "rb").read()
    iterator = iter(bytes_read)
    poly_line_index = 0
    height = int(1000 * scale)
    width = int(1800 * scale)
    frame = np.ones((height,width,3), np.uint8)
    output_size = (width, height)

    codec = cv2.VideoWriter_fourcc('M','J','P','G')
    fps = 15
    videof = cv2.VideoWriter()
    success = videof.open('cli.avi',codec,fps,output_size,True) 
    print "video file was created with return value " + str(success)

    try:
        b = iterator.next()
        while True:
            if(Binary):   
                intb = int(b.encode('hex_codec'), 16) 
                #  print b.encode('hex_codec')
                b = iterator.next()
                nextb = int(b.encode('hex_codec'), 16)
 
                if((intb == 127) and (nextb == 0)):
                    z1 = iterator.next()
                    z2 = iterator.next()
                    z3 = iterator.next()
                    z4 = iterator.next()
                    zheight = z4 + z3 + z2 + z1 
                    zheight = struct.unpack('>f',zheight)[0] * 0.01   
                    frame = np.ones((height,width,3), np.uint8)
                    if (len(poly_lines) and len(directions)):
                        for l1, d1 in itertools.izip(poly_lines, directions):
                            if d1 == 1:
                                cv2.fillPoly(frame,[l1],(255,255,255))
                            if d1 == 0: 
                                cv2.fillPoly(frame,[l1],(0,0,0))
                    layers.append(poly_lines)
                    layer_directions.append(directions)
                    
                    directions = []
                    poly_lines = []
                    text_string1 = "Youngstown State University"
                    text_string2 = "Z Height=" + str(float(zheight))
                    text_string3 = "CLI Cracker"
                    cv2.putText(frame, text_string1, (230, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
                    cv2.putText(frame, text_string3, (400, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                    cv2.putText(frame, text_string2, (635, 450), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                    cv2.imshow("window",frame)
                    videof.write(frame)

                if((intb == 130) and (nextb == 0)):
                    z1 = iterator.next()
                    z2 = iterator.next()
                    z3 = iterator.next()
                    z4 = iterator.next()
                    idx = z4 + z3 + z2 + z1
                    idx = struct.unpack('>L',idx)[0]
                    z1 = iterator.next()
                    z2 = iterator.next()
                    z3 = iterator.next()
                    z4 = iterator.next()
                    direction = z4 + z3 + z2 + z1
                    direction = struct.unpack('>L',direction)[0]
                    #print direction
                    directions.append(direction)
                    z1 = iterator.next()
                    z2 = iterator.next()
                    z3 = iterator.next()
                    z4 = iterator.next()
                    npts = z4 + z3 + z2 + z1
                    npts = struct.unpack('>L',npts)[0]
                    poly_line = []
                    while (npts > 0):
                        x1 = iterator.next()
                        x2 = iterator.next()
                        x3 = iterator.next()
                        x4 = iterator.next()
                        x = x4 + x3 + x2 + x1 
                        x = struct.unpack('>f',x)[0]  
                        x = int(x*scale/100)
                        y1 = iterator.next()
                        y2 = iterator.next()
                        y3 = iterator.next()
                        y4 = iterator.next()
                        y = y4 + y3 + y2 + y1 
                        y = struct.unpack('>f',y)[0]  
                        y = int(y*scale/100)
                        npts = npts - 1
                        poly_line.append((x,y))
                    poly_line = np.array( poly_line, dtype=np.int32 )
                    poly_lines.append(poly_line)  
                    b = iterator.next()
		
            if(ASCII):   
                dq1.append(b)
                dq1.popleft()
                b = iterator.next()
                if(dq1 == dq2):
                    print "found the end of ASCII"
                    ASCII = False
                    Binary = True
    except StopIteration:
        pass

    return layers, layer_directions




def cli_readerascii( fileinput ):

    scale = 0.5
    fileinput =  sys.argv[1]
    #bytes_read = open(fileinput, "rb").read()
    poly_line_index = 0

    height = int(1000 * scale)
    width = int(1800 * scale)
    frame = np.ones((height,width,3), np.uint8)
    output_size = (width, height)

    codec = cv2.VideoWriter_fourcc('M','J','P','G')
    fps = 2 
    videof = cv2.VideoWriter()
    success = videof.open('cli.avi',codec,fps,output_size,True) 

    dq1 = deque(['.','.','H','E','A','D','E','R','E','N','D'])
    dq2 = deque(['$','$','H','E','A','D','E','R','E','N','D'])
    first_layer = True
    l = []
    l1 = []
    poly_lines = []
    directions = []

    try:
        with open(fileinput) as fp:
            for data_line in fp:
                data = data_line.split('/')
            #            print data[0] + "command"
                if(data[0] == '$$LAYER'):
                    #                print "new layer"
                    z_height = data[1]
                    #                print data[1] + "height"
                    # zheight = struct.unpack('>f',zheight)[0] * 0.01   # CLI file is in 0.01 mm increments                                                   
                    frame = np.ones((height,width,3), np.uint8)
                    if (first_layer):
                        first_layer = False
                    else:
                        #                    print "poly lines " + str(len(poly_lines))
                        #                    print "directions " + str(len(directions))
                        for l1, d1 in itertools.izip(poly_lines, directions):
                            #                        print d1
                            if d1 == '1':
                                #                            print l1
                                cv2.fillPoly(frame,[l1],(255,255,255))
                            elif d1 == '0': 
                                cv2.fillPoly(frame,[l1],(0,0,0))
                            else:
                                print "direction not 1 or 0"
                                layers.append(poly_lines)
                                layer_directions.append(directions) 
                                directions = []
                                text_string1 = "Youngstown State University"
                                text_string2 = "Z Height=" + str(float(z_height))
                                text_string3 = "CLI Cracker"
                                cv2.putText(frame, text_string1, (230, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
                                cv2.putText(frame, text_string3, (400, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                                cv2.putText(frame, text_string2, (635, 450), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                                cv2.imshow("window",frame)
                                cv2.waitKey(1)
                                videof.write(frame)
                                poly_lines = []
        
                                if(data[0] == '$$POLYLINE'):
                                    lines = data[1].split(',') 
                                    #                print "line length " + str(len(data))
                                    #                print lines
                                    id = lines[0]
                                    direction = lines[1]
                                    directions.append(direction)
                                    npts = (int(lines[2]))
                                    index = 3
                                    poly_line = []
                                    while (npts > 0):
                                        #                    print lines[index] 
                                        #                    print lines[index+1] 
                                        #                    print type(lines[index])
                                        x = 2*math.floor(float(lines[index]))
                                        index = index + 1
                                        y = 2*math.floor(float(lines[index]))
                                        index = index + 1 
                                        npts = npts - 1 
                    #                   print "npts" + str(npts)
                                        poly_line.append((x,y))
                                        poly_line = np.array( poly_line, dtype=np.int32)
                                        poly_lines.append(poly_line)
                        
                        
    except StopIteration:
        pass
    return layers, layer_directions




def draw_layer( index, layers, layer_directions ):
    polylines = layers[index]
    directions = layer_directions[index]
    text_string1 = "Youngstown State University"
    text_string2 = "Z Height=" + str(float(zheight))
    text_string3 = "CLI Cracker"
    cv2.putText(frame, text_string1, (230, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
    cv2.putText(frame, text_string2, (635,450), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
    cv2.putText(frame, text_string3, (400, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
    
    frame = draw_layer(5)
    layer_string = 'layer ' + str(index)
    cv2.imshow(layer_string , frame)
    cv2.waitKey(0)
    
    return frame
