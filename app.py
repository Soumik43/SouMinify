import streamlit as st
import os
import functions
import firebase_admin
import config

from firebase_admin import storage, initialize_app, credentials
from model import imageCompression
from utils import allFormats

if not firebase_admin._apps:
    cred = credentials.Certificate('serviceAccountKey.json')
    initialize_app(cred, {
        'storageBucket': config.FIREBASE_STORAGE_LINK,
    })

bucket = storage.bucket()


st.write("""
    # Image Compression
""")

menu = ["Upload Image", "Retrieve Image"]
selectedHeader = st.sidebar.selectbox(
    'Select function',
    menu,
    help='Choose which function you would like to work with!'
)


if selectedHeader == menu[0]:
    st.write('''
    ## Upload Files
    Supported files types will be compressed in JPG format and will be uploaded in cloud.
    ''')
    file = st.file_uploader("Upload image", type=allFormats)
    if file:
        st.write("""
        ### Original image
        """)
        st.image(file)

        # Image compression model
        st.write("""
        ### Compressed image
        """)
        compressedImage = imageCompression(file)

        # Find file Prefix
        filePrefix = file.name[:file.name.find('.')]

        # Store image
        blob = bucket.blob(f'Images/{filePrefix}.jpg')
        blob.upload_from_filename(f'{filePrefix}_out.jpg')

        if os.path.isfile(f"{filePrefix}_out.jpg"):
            os.remove(f"{filePrefix}_out.jpg")
else:
    st.write('''
        ## Retrieve files from cloud
        Files that are compressed will be stored on cloud and can be retrieved back.
    ''')

    # Retrieve image in cloud
    functions.retrieveImage(bucket)
