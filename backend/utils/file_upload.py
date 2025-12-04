import os
import zipfile
import uuid

def extract_zip(file):
    upload_folder = "uploads"
    os.makedirs(upload_folder, exist_ok=True)
    uid = str(uuid.uuid4())
    extract_path = os.path.join(upload_folder, uid)
    os.makedirs(extract_path, exist_ok=True)

    zip_path = os.path.join(upload_folder, uid + ".zip")
    file.save(zip_path)
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_path)
    return extract_path
