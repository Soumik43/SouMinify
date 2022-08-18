
# Image JPEG compression

This is an Image compressor which uses algorithms like **Huffman tree, Quantization, DCT** inorder to compress images.


The images that are compressed are stored in cloud, here firebase storage has been used for the storing the images.




## Run Locally

Clone the project

```bash
  git clone https://link-to-project
```

Go to the project directory

```bash
  cd my-project
```

Install requirements text file

```bash
  pip install -r requirements.txt
```

Create a firebase project and create a **Web app**, download the json file given, name it 
**serviceAccountKey.json** and paste it in our folder directory.

```bash
  myProject/serviceAccountKey.json
```

Create a storage bucket in your firebase console, and get the link to the
 storage (exclude the gs://) and use in the **app.py** file.

```bash
  initialize_app(cred, {
        'storageBucket': '{Your link to the firebase storage}'
    })
```

Start the streamlit server

```bash
  streamlit run app.py
```

