
# Image JPEG compression

Look at the live working website right here - [Image JPEG Compression](https://soumik43-image-jpeg-compression-app-220kaa.streamlitapp.com/) 


This is an Image compressor that uses algorithms like **Huffman tree, Quantization, and DCT** which are also used in Whatsapp image compression, in order to compress images.


The images that are compressed are stored in cloud, here firebase storage has been used for the storing the images.




## Run Locally

Clone the project

```bash
  git clone https://github.com/Soumik43/Image-Jpeg-Compression
```

Go to the project directory

```bash
  cd image-jpeg-compression
```

Install requirements text file

```bash
  pip install -r requirements.txt
```

Create a new firebase project and create a **Web app**, download the json file given, name it **serviceAccountKey.json** and paste it in your folder directory.

```bash
  image-jpeg-compression/serviceAccountKey.json

```

Create a storage bucket in your firebase console, and get the link to the storage (exclude the gs:// from the link) and use in the **app.py** file.

```bash
  Paste your link like given below in file app.py
  
  initialize_app(cred, {
        'storageBucket': '{Your link to the firebase storage}'
    })
```

Start the streamlit server

```bash
  streamlit run app.py
```

Inorder to change the limit of the upload size in streamlit while image selection, you can change this in the .streamlit/config.toml file.

```bash
  [server]
  maxUploadSize = {Your upload limit size}
```