import streamlit as st
import math
import os
import numpy as np

from firebase import storage
from PIL import Image


def convertToWebp(source: str, imageFile):
    dotPos = source.find('.')
    if dotPos != -1:
        destination = source[:source.find('.')] + '.webp'
    else:
        destination = source+'.webp'
    image = Image.open(imageFile)
    image.save(destination, format="webp")
    return Image.open(destination)


def rgb2ycbcr(im):
    xform = np.array(
        [[.299, .587, .114], [-.1687, -.3313, .5], [.5, -.4187, -.0813]])
    ycbcr = im.dot(xform.T)

    ycbcr[:, :, [1, 2]] += 128

    return np.uint8(ycbcr)


def prettySize(sizeBytes):
    if sizeBytes == 0:
        return "0B"
    sizeName = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = int(math.floor(math.log(sizeBytes, 1024)))
    p = math.pow(1024, i)
    s = round(sizeBytes / p, 2)
    return "%s %s" % (s, sizeName[i])


def retrieveImage(bucket: storage.Bucket):
    with st.form('firebaseQuery'):
        newQuery = st.text_input(label='Image name')
        submit = st.form_submit_button('Retrieve')
        if submit and newQuery:
            allImages = bucket.list_blobs()
            allImagesNames = [img.name for img in allImages]
            imageFound = 0
            for name in allImagesNames:
                if f'{newQuery}.jpg' == name[name.find('/')+1:]:
                    path = f'Images/{newQuery}.jpg'
                    imageBlob = bucket.blob(path)
                    imageBlob.download_to_filename(f'{newQuery}.jpg')
                    imageFound = 1
                    break
            if imageFound:
                st.image(f'{newQuery}.jpg')
                if os.path.isfile(f'{newQuery}.jpg'):
                    os.remove(f'{newQuery}.jpg')
            else:
                st.error('Image not found')
        elif submit:
            st.error('Empty image name')


def zigzag(array: np.ndarray) -> np.ndarray:
    h = 0
    v = 0
    vMin = 0
    hMin = 0
    vMax = array.shape[0]
    hMax = array.shape[1]
    i = 0
    output = np.zeros((vMax * hMax))
    while (v < vMax) and (h < hMax):
        if ((h + v) % 2) == 0:
            if v == vMin:
                output[i] = array[v, h]
                if h == hMax:
                    v = v + 1
                else:
                    h = h + 1
                i = i + 1
            elif (h == hMax - 1) and (v < vMax):
                output[i] = array[v, h]
                v = v + 1
                i = i + 1
            elif (v > vMin) and (h < hMax - 1):
                output[i] = array[v, h]
                v = v - 1
                h = h + 1
                i = i + 1
        else: 
            if (v == vMax - 1) and (h <= hMax - 1):
                output[i] = array[v, h]
                h = h + 1
                i = i + 1
            elif h == hMin:
                output[i] = array[v, h]
                if v == vMax - 1:
                    h = h + 1
                else:
                    v = v + 1
                i = i + 1
            elif (v < vMax - 1) and (h > hMin):
                output[i] = array[v, h]
                v = v + 1
                h = h - 1
                i = i + 1
        if (v == vMax - 1) and (h == hMax - 1):
            output[i] = array[v, h]
            break

    return output


def getHuffmanCode(huff):
    [print(f"{key_value[0]}\t{key_value[1]}") for key_value in huff]
