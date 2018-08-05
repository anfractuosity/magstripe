#!/usr/bin/python3

import numpy as np
from scipy import ndimage
from scipy import misc
import matplotlib.pyplot as plt
import math


def avg(l):
    return math.ceil(float(sum(l))/len(l) if len(l) > 0 else float('nan'))


def process(jpg):

    card = misc.imread(jpg, flatten=1)
    card = card > card.mean()
    width = card.shape[1]
    height = card.shape[0]

    arr = np.zeros((width))

    # Create array to represent possible magnetic field lines
    for y in range(0, height):
        for x in range(0, width):
            if card[y][x]:
                arr[x] = arr[x]+1

    z = 0
    arr2 = []
    for e in arr:
        # if >90% of pixels in column are 'on' likely part of magnetic line
        if e > ((height/100)*90):
            arr2.append(z)
        z = z + 1

    old = -1

    width = 0

    l = []

    mx = -1
    mxl = []

    for z in arr2:
        if not old == -1:
            mxl.append(int(z-old))
        if z == old+1:
            width = width + 1
        else:
            if width > 0:
                l.append(width)
            width = 0
        old = z
    mxl.sort()

    # Separation between lines need to classify as 0s
    sepdist = avg(mxl[-int((len(mxl)/100)*20):])

    # Width in pixels of magnetic field line
    maxstripewidth = avg(l)

    arr3 = []
    arr3b = []

    for z in arr2:
        if z > old+maxstripewidth:
            arr3.append(z)
            arr3b.append(height/2)
        old = z

    old = 0

    arr4 = []

    bitstr = ""
    marker = 0
    for i in range(0, len(arr3)):
        if i > 0:
            if arr3[i]-arr3[i-1] > sepdist:
                bitstr = bitstr + "0"
                marker = 0
            else:
                marker = marker + 1
                if marker == 2:
                    bitstr = bitstr + "1"
                    marker = 0

    bcd = {"10000": "0",
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
           "11111": "?"}

    posi = []
    for z in range(0, len(bitstr)):
        if bitstr[z:z+5] == "11111":
            out = ""
            q = z
            while True:
                chunk = bitstr[q:q+5]
                if len(chunk) == 5:
                    if chunk not in bcd:
                        break
                    out = bcd[chunk] + out
                else:
                    break
                q = q + 5
            posi.append(out)

    print("Card:", max(posi, key=len))
    plt.scatter(arr3, arr3b)
    plt.imshow(card)
    plt.show()


process("magstripe.jpg")
