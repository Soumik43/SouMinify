import numpy as np

from math import ceil
from scipy.fftpack import dct
from functions import zigzag
from scipy.signal import convolve2d


QTY = np.array([
    [16, 11, 10, 16, 24, 40, 51, 61],
    [12, 12, 14, 19, 26, 48, 60, 55],
    [14, 13, 16, 24, 40, 57, 69, 56],
    [14, 17, 22, 29, 51, 87, 80, 62],
    [18, 22, 37, 56, 68, 109, 103, 77],
    [24, 35, 55, 64, 81, 104, 113, 92],
    [49, 64, 78, 87, 103, 121, 120, 101],
    [72, 92, 95, 98, 112, 100, 103, 99]
])

QTC = np.array([
    [17, 18, 24, 47, 99, 99, 99, 99],
    [18, 21, 26, 66, 99, 99, 99, 99],
    [24, 26, 56, 99, 99, 99, 99, 99],
    [47, 66, 99, 99, 99, 99, 99, 99],
    [99, 99, 99, 99, 99, 99, 99, 99],
    [99, 99, 99, 99, 99, 99, 99, 99],
    [99, 99, 99, 99, 99, 99, 99, 99],
    [99, 99, 99, 99, 99, 99, 99, 99]
])


def sample(y, cr, cb):
    y = y - 128
    cr = cr - 128
    cb = cb - 128

    SSH, SSV = 2, 2
    kernel = np.array([[0.25, 0.25], [0.25, 0.25]])

    cr = np.repeat(np.repeat(convolve2d(cr, kernel, mode='valid')[
                   ::SSV, ::SSH], 2, axis=0), 2, axis=1)
    cb = np.repeat(np.repeat(convolve2d(cb, kernel, mode='valid')[
                   ::SSV, ::SSH], 2, axis=0), 2, axis=1)

    return y, cr, cb


def getZigzags(y, cr, cb, windowSize):
    hbC = int(len(y[0]) / windowSize)
    vbY = int(len(y) / windowSize)
    hbC = int(len(cr[0]) / windowSize)
    vbC = int(len(cr) / windowSize)

    yZigzag = np.zeros(((vbY * hbC), windowSize * windowSize))
    crZigzag = np.zeros(((vbC * hbC), windowSize * windowSize))
    cbZigzag = np.zeros(((vbC * hbC), windowSize * windowSize))

    for i in range(vbY):
        for j in range(hbC):
            yZigzag[i * j] += zigzag(
                y[i * windowSize: i * windowSize + windowSize,
                    j * windowSize: j * windowSize + windowSize]
            )
    yZigzag = yZigzag.astype(np.int16)

    for i in range(vbC):
        for j in range(hbC):
            crZigzag[i * j] += zigzag(
                cr[i * windowSize: i * windowSize + windowSize,
                    j * windowSize: j * windowSize + windowSize]
            )
            cbZigzag[i * j] += zigzag(
                cb[i * windowSize: i * windowSize + windowSize,
                    j * windowSize: j * windowSize + windowSize]
            )
    crZigzag = crZigzag.astype(np.int16)
    cbZigzag = cbZigzag.astype(np.int16)

    return yZigzag, crZigzag, cbZigzag


def performDct(y, cr, cb, yWidth, yLength, cWidth, cLength, windowSize):
    yDct, crDct, cbDct = np.zeros((yLength, yWidth)), np.zeros(
        (cLength, cWidth)), np.zeros((cLength, cWidth))

    hbY = int(len(yDct[0]) / windowSize)
    vbY = int(len(yDct) / windowSize)
    hbC = int(len(crDct[0]) / windowSize)
    vbC = int(len(crDct) / windowSize)

    for i in range(vbY):
        for j in range(hbY):
            yDct[i * windowSize: i * windowSize + windowSize, j * windowSize: j * windowSize + windowSize] = dct(
                y[i * windowSize: i * windowSize + windowSize,
                    j * windowSize: j * windowSize + windowSize],
                norm='ortho'
            )

    # either crq or cbq can be used to compute the number of blocks
    for i in range(vbC):
        for j in range(hbC):
            crDct[i * windowSize: i * windowSize + windowSize, j * windowSize: j * windowSize + windowSize] = dct(
                cr[i * windowSize: i * windowSize + windowSize,
                    j * windowSize: j * windowSize + windowSize],
                norm='ortho'
            )
            cbDct[i * windowSize: i * windowSize + windowSize, j * windowSize: j * windowSize + windowSize] = dct(
                cb[i * windowSize: i * windowSize + windowSize,
                    j * windowSize: j * windowSize + windowSize],
                norm='ortho'
            )

    return yDct, crDct, cbDct


def givePaddings(y, cr, cb, windowSize):
    yWidth, yLength = ceil(len(y[0]) / windowSize) * \
        windowSize, ceil(len(y) / windowSize) * windowSize

    if (len(y[0]) % windowSize == 0) and (len(y) % windowSize == 0):
        yPadded = y.copy()
    else:
        yPadded = np.zeros((yLength, yWidth))
        for i in range(len(y)):
            for j in range(len(y[0])):
                yPadded[i, j] += y[i, j]

    cWidth, cLength = ceil(len(cb[0]) / windowSize) * \
        windowSize, ceil(len(cb) / windowSize) * windowSize
    if (len(cb[0]) % windowSize == 0) and (len(cb) % windowSize == 0):
        crPadded = cr.copy()
        cbPadded = cb.copy()
    else:
        crPadded = np.zeros((cLength, cWidth))
        cbPadded = np.zeros((cLength, cWidth))
        for i in range(len(cr)):
            for j in range(len(cr[0])):
                crPadded[i, j] += cr[i, j]
                cbPadded[i, j] += cb[i, j]

    return yPadded, crPadded, cbPadded, yWidth, yLength, cWidth, cLength


def quantize(y, cr, cb):
    windowSize = len(QTY)
    y, cr, cb, yWidth, yLength, cWidth, cLength = givePaddings(
        y, cr, cb, windowSize)

    yDct, crDct, cbDct = performDct(
        y, cr, cb, yWidth, yLength, cWidth, cLength, windowSize)

    yq, crq, cbq = np.zeros((yLength, yWidth)), np.zeros(
        (cLength, cWidth)), np.zeros((cLength, cWidth))

    hbY = int(len(yDct[0]) / windowSize)
    vbY = int(len(yDct) / windowSize)
    hbC = int(len(crDct[0]) / windowSize)
    vbC = int(len(crDct) / windowSize)

    for i in range(vbY):
        for j in range(hbY):
            yq[i * windowSize: i * windowSize + windowSize, j * windowSize: j * windowSize + windowSize] = np.ceil(
                yDct[i * windowSize: i * windowSize + windowSize,
                     j * windowSize: j * windowSize + windowSize] / QTY
            )

    for i in range(vbC):
        for j in range(hbC):
            crq[i * windowSize: i * windowSize + windowSize, j * windowSize: j * windowSize + windowSize] = np.ceil(
                crDct[i * windowSize: i * windowSize + windowSize,
                      j * windowSize: j * windowSize + windowSize] / QTC
            )
            cbq[i * windowSize: i * windowSize + windowSize, j * windowSize: j * windowSize + windowSize] = np.ceil(
                cbDct[i * windowSize: i * windowSize + windowSize,
                      j * windowSize: j * windowSize + windowSize] / QTC
            )

    print(f'Total number of operations: {vbC * hbC + vbY * hbY}')

    return yq, crq, cbq, windowSize
