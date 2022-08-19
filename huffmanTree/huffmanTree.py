import numpy as np

from collections import deque


class PriorityQueue:
    def __init__(self):
        self.queue = []

    def push(self, huffmanTreeCell):
        self.queue.append(huffmanTreeCell)
        self.queue.sort(key=lambda h: h.freq, reverse=True)

    def pop(self):
        return self.queue.pop()

    def top(self):
        return self.queue[-1]

    def size(self):
        return len(self.queue)


class HuffmanTreeCell:
    def __init__(self):
        self.data = None
        self.freq = None
        self.left = None
        self.right = None


def generateEncoding(root, code):
    if root.left == None and root.right == None:
        yield (root.data, code)
        return
    yield from generateEncoding(root.left, code+"0")
    yield from generateEncoding(root.right, code+"1")


def generateCell(root, encoded, value):
    if len(encoded) == 0:
        root.data = value
        return
    s = encoded.pop()
    if s == '0' and root.left == None:
        new_cell = HuffmanTreeCell()
        root.left = new_cell
        generateCell(root.left, encoded, value)
    elif s == '0' and root.left != None:
        generateCell(root.left, encoded, value)
    elif s == '1' and root.right == None:
        new_cell = HuffmanTreeCell()
        root.right = new_cell
        generateCell(root.right, encoded, value)
    elif s == '1' and root.right != None:
        generateCell(root.right, encoded, value)


def generateHuffmanTreeFromEncoding(huffmanEncoding, root=None):
    if root == None:
        root = HuffmanTreeCell()
    for value, encoded in huffmanEncoding:
        encoded = list(encoded)
        encoded.reverse()
        generateCell(root, encoded, value)
    return root


def decodeHuffmanEncoding(huffmanEncoding, encodedData):
    root = generateHuffmanTreeFromEncoding(huffmanEncoding)
    decoded_data = ''
    encodedData = list(encodedData)
    encodedData.append('0')
    encodedData.reverse()

    def startDecode(root, encodedData):
        s = encodedData[-1]
        if s == '0' and root.left != None:
            encodedData.pop()
            return startDecode(root.left, encodedData)
        elif s == '0' and root.left == None:
            return encodedData, root.data
        elif s == '1' and root.right != None:
            encodedData.pop()
            return startDecode(root.right, encodedData)
        elif s == '1' and root.right == None:
            return encodedData, root.data
    while len(encodedData) > 1:
        encodedData, decoded = startDecode(root, encodedData)
        decoded_data += decoded
    return decoded_data


def huffmanImageDecoder(encodedValue, nDim=None):

    def decodeHeader(encodedValue):
        totalLastPad = int(encodedValue[0:8], 2)
        width = int(encodedValue[8:40], 2)
        height = int(encodedValue[40:72], 2)
        totalMapData = int(encodedValue[72:80], 2) + 1
        huffmanEncoding = []
        i = 80
        count = 0
        while 1:
            originalVal = int(encodedValue[i:i+8], 2)
            totalPad = int(encodedValue[i+8:i+16], 2)
            byteLength = int(encodedValue[i+16:i+24], 2)
            i = i + 24
            padEncVal = encodedValue[i: i+byteLength*8]
            encVal = padEncVal[totalPad:]
            huffmanEncoding.append((originalVal, encVal))
            i = i + (byteLength*8)
            count += 1
            if count == totalMapData:
                break
        encodedData = encodedValue[i:-totalLastPad]
        return width, height, huffmanEncoding, encodedData

    width, height, huffmanEncoding, encodedData = decodeHeader(encodedValue)
    root = generateHuffmanTreeFromEncoding(huffmanEncoding)
    decoded_data = deque()
    encodedData = deque(encodedData)
    encodedData.append('0')

    def startDecode(root: HuffmanTreeCell, encodedData):
        s = encodedData[0]
        if s == '0' and root.left != None:
            encodedData.popleft()
            return startDecode(root.left, encodedData)
        elif s == '0' and root.left == None:
            return root.data
        elif s == '1' and root.right != None:
            encodedData.popleft()
            return startDecode(root.right, encodedData)
        elif s == '1' and root.right == None:
            return root.data
    try:
        while 1:
            decoded = startDecode(root, encodedData)
            decoded_data.append(decoded)
    except Exception:
        pass
    arrImg = np.array(decoded_data)
    if nDim:
        arrImg = arrImg.reshape(height, width, nDim)
    else:
        arrImg = arrImg.reshape(height, width)
    return arrImg


def huffman(valueFrequency):
    queue = PriorityQueue()
    for data, freq in valueFrequency:
        treeCell = HuffmanTreeCell()
        treeCell.data = data
        treeCell.freq = freq
        treeCell.left = None
        treeCell.right = None
        queue.push(treeCell)
    root = None
    while queue.size() > 1:
        x = queue.pop()
        y = queue.pop()
        f = HuffmanTreeCell()
        f.data = '-'
        f.freq = x.freq + y.freq
        f.left = x
        f.right = y
        root = f
        queue.push(f)
    try:
        yield from generateEncoding(root, "")
    except:
        root = queue.pop()
        yield (root.data, "0")


def toBytes(data):
    for i in range(0, len(data), 8):
        yield bytes([int(data[i:i+8], 2)])


def wrapEncodedData(huffmanMap, encodedData, width, height, y, cr, cb):
    encodedData = ''.join(list(encodedData))
    totalLastBitPad = 8-len(encodedData) % 8
    bTotalLastBitPad = '{0:08b}'.format(totalLastBitPad)
    width = '{0:032b}'.format(width)
    height = '{0:032b}'.format(height)
    totalMapData = '{0:08b}'.format(len(huffmanMap)-1)
    header = bTotalLastBitPad + width + height + totalMapData
    mapData = ''
    for originalVal, encVal in huffmanMap:
        bOriginalVal = '{0:08b}'.format(originalVal)
        totalPad = 8-len(encVal) % 8
        bTotalPad = '{0:08b}'.format(totalPad)
        bEncodedVal = totalPad*'0' + encVal
        byteLength = '{0:08b}'.format(int(len(bEncodedVal)/8))
        mapData = mapData + bOriginalVal + bTotalPad + byteLength + bEncodedVal
    header = header + mapData
    lastBitPad = totalLastBitPad * '0'
    wrappedData = header + encodedData + lastBitPad
    return wrappedData


def encodePixelValue(huffmanMap, img_array):
    huffmanMapDict = {keyValue[0]: keyValue[1] for keyValue in huffmanMap}
    encodedPixels = (huffmanMapDict[px] for px in img_array)
    return encodedPixels
