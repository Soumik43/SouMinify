import os
import time
import huffmanTree.huffmanTree as huffman
import numpy as np
import streamlit as st
import quantization.quantization as quantizationProcess
import functions

from PIL import Image


def imageCompression(image):
    myBar = st.progress(0)
    fileName = image.name
    fileSuffix = fileName[:fileName.find('.')]

    ogImage = Image.open(image)
    RGBImage = ogImage.convert('RGB')
    webpImagePath = fileSuffix+'.webp'
    ogImgSize = len(Image.open(image).fp.read())

    if fileName[fileName.find('.') + 1:] != '.webp':
        im = functions.convertToWebp(fileName, image)
    else:
        im = ogImage
    imArr = np.asarray(im)
    imArrRGB = np.asarray(RGBImage)
    imArrRGB = functions.rgb2ycbcr(imArrRGB)
    myBar.progress(7)

    try:
        height, width, dim = imArr.shape
    except ValueError:
        height, width = imArr.shape
        dim = None

    y = np.zeros((height, width), np.float32)+imArrRGB[:, :, 0]
    cr = np.zeros((height, width), np.float32)+imArrRGB[:, :, 1]
    cb = np.zeros((height, width), np.float32)+imArrRGB[:, :, 2]

    # Sampling
    y, cr, cb = quantizationProcess.sample(y, cr, cb)
    print(f'Chroma subsampling done')
    myBar.progress(23)

    # quantizing
    y, cr, cb, ws = quantizationProcess.quantize(y, cr, cb)
    print(f'Quantization done')
    myBar.progress(40)

    # zigzags
    y, cr, cb = quantizationProcess.getZigzags(y, cr, cb, ws)
    print(f'ZigZag iteration done')
    myBar.progress(57)

    compressedImagePath = f"{fileSuffix}_out.jpg"

    encodeStartTime = time.time()

    imGrayflat = imArr.ravel()
    hist = np.bincount(imGrayflat)
    prob = hist/np.sum(hist)

    valueFreq = ((v, f) for v, f in enumerate(prob) if f > 0)
    huffmanMap = list(huffman.huffman(valueFreq))

    # Encode image
    encodedPixel = huffman.encodePixelValue(huffmanMap, imGrayflat)

    bytesGenerator = huffman.toBytes(
        huffman.wrapEncodedData(huffmanMap,
                                encodedPixel,
                                width,
                                height,
                                y,
                                cb,
                                cr)
    )
    with open(f"{fileSuffix}.huff", "wb") as f:
        for data in bytesGenerator:
            f.write(data)
    myBar.progress(74)

    encodeStopTime = time.time()

    decodeStartTime = time.time()

    with open(f"{fileSuffix}.huff", "rb") as f:
        enc_img = f.read()

    compressedHuffmanPath = f"{fileSuffix}.huff"

    # decode image
    bEncImg = ''.join(map(lambda x: '{:08b}'.format(x), enc_img))
    arrImg = huffman.huffmanImageDecoder(bEncImg, dim)
    arrImg = arrImg.astype('uint8')
    myBar.progress(90)

    # Save image after decoding/compression
    rawImg = Image.fromarray(arrImg)
    rawImg.save(compressedImagePath)

    decodeStopTime = time.time()

    jpgImageSize = os.path.getsize(compressedImagePath)
    compressedSize = ((ogImgSize - jpgImageSize)/ogImgSize)*100
    st.write(
        f'Compressed image size (JPG) : **{functions.prettySize(jpgImageSize)}**')

    # Show compressed image
    st.image(compressedImagePath)

    # Remove files stored
    if os.path.isfile(webpImagePath):
        os.remove(webpImagePath)
    if os.path.isfile(compressedHuffmanPath):
        os.remove(compressedHuffmanPath)

    st.subheader(
        f'Optimal compression score percentage : **{compressedSize.__round__(2)}%**')

    myBar.progress(100)
    st.success(
        f'Image compressed and uploaded! Total time taken : **{(encodeStopTime - encodeStartTime) + (decodeStopTime - decodeStartTime)} seconds**')
    st.balloons()
