#!/usr/bin/python3

# Optical decoding of track 2 of a credit card
#
# https://www.anfractuosity.com/projects/optical-magnetic-stripe-reading/

import argparse
import numpy as np
from scipy import ndimage
from scipy import misc
import matplotlib.pyplot as plt
import math
import sys
import os

# Average
def avg(l):
    return math.ceil(float(sum(l)) / len(l) if len(l) > 0 else float("nan"))


# Process credit card image and return numeric data
def process(jpg):

    if not os.path.exists(jpg):
        print("Please provide an image that exists",file=sys.stderr)
        return

    # Read image and threshold it
    card = misc.imread(jpg, flatten=1)
    card = card > card.mean()

    width = card.shape[1]
    height = card.shape[0]

    pixels = np.zeros((width))

    # Create array to represent possible magnetic field lines
    for y in range(0, height):
        for x in range(0, width):
            if card[y][x]:
                pixels[x] = pixels[x] + 1
    lines = []

    # Record the x position of each line
    for i in range(len(pixels)):
        # if >90% of pixels in column are 'on' likely part of magnetic line
        if pixels[i] > ((height / 100) * 90):
            lines.append(i)

    lastlinepos = -1
    width = 0
    sep = []
    widths = []

    # Create a list of the widths, between lines
    for linepos in lines:

        if not lastlinepos == -1:
            widths.append(int(linepos - lastlinepos))

        lastlinepos = linepos

    widths = sorted(widths)

    # Separation between lines need to classify as 0s
    sepdist = avg(widths[-int((len(widths)/100)*20):])

    # Width in pixels of magnetic field line
    maxstripewidth = avg(widths)

    old = 0 # last line position
    pos = [] # position of lines
    yaxis = [] # y axis value for 'dot' for visualisation

    # Create list of line positions above a certain width 
    for lpos in lines:
        if lpos > old+maxstripewidth:
            pos.append(lpos)
            yaxis.append(height/2)
        old = lpos

    bitstr = ""
    marker = 0
   
    # Generate binary data as a string
    for i in range(0, len(pos)):
        if i > 0:
            if pos[i]-pos[i-1] > sepdist:
                bitstr = bitstr + "0"
                marker = 0
            else:
                marker = marker + 1
                if marker == 2:
                    bitstr = bitstr + "1"
                    marker = 0
   
    # Mapping of binary data
    bcd = {
        "10000": "0",
        "00001": "1",
        "00010": "2",
        "10011": "3",
        "00100": "4",
        "10101": "5",
        "10110": "6",
        "00111": "7",
        "01000": "8",
        "11001": "9",
        "11010": ":",
        "01011": ";",
        "11100": "<",
        "01101": "=",
        "01110": ">",
        "11111": "?",
    }

    possible = []   # possible card numbers
    start = "11111" # card starts with

    for x in range(0, len(bitstr)):
        if bitstr[x : x + len(start)] == start: # found potential start
            out = ""
            q = x
            while True:
                chunk = bitstr[q : q + len(start)]
                if len(chunk) == len(start):
                    if chunk not in bcd:
                        break
                    out = bcd[chunk] + out
                else:
                    break
                q += len(start)
            possible.append(out)

    print("Card:", max(possible, key=len)) # print card number with longest length

    plt.scatter(pos, yaxis)
    plt.imshow(card)
    plt.show() # show visualisation

parser = argparse.ArgumentParser()
parser.add_argument("image", help="Filename of track 2 of a credit card image")
args = parser.parse_args()

process(args.image)
