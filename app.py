import streamlit as st
import os
import functions
import firebase_admin

from firebase_admin import storage, initialize_app, credentials
from model import imageCompression
from utils import allFormats

if not firebase_admin._apps:
    fbCred = st.secrets.firebase_credentials
    credentialsToml = {
        "type": fbCred.type,
        "project_id": fbCred.project_id,
        "private_key_id": fbCred.private_key_id,
        "private_key": fbCred.private_key,
        "client_email": fbCred.client_email,
        "client_id": fbCred.client_id,
        "auth_uri": fbCred.auth_uri,
        "token_uri": fbCred.token_uri,
        "auth_provider_x509_cert_url": fbCred.auth_provider_x509_cert_url,
        "client_x509_cert_url": fbCred.client_x509_cert_url
    }
    cred = credentials.Certificate(credentialsToml)
    initialize_app(cred, {
        'storageBucket': st.secrets.db_credentials.FIREBASE_STORAGE_LINK,
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
