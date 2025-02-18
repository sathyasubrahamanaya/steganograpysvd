from fastapi import APIRouter, Depends, HTTPException, status, UploadFile,File
from PIL import Image
import datetime
import io
from .core import algorithm,zipfiles
import zipfile
import os
import cv2
import joblib
from app.models import User
from fastapi.responses import FileResponse
from app.core import algorithm
from starlette.background import BackgroundTask
import tempfile
from app.security import get_current_user
decrpyt_router = APIRouter()

def clean_storage(file_name):
    os.remove(file_name)

@decrpyt_router.post("/decrypt")
async def decrypt(input_file:UploadFile=File(...),current_user:User = Depends(get_current_user)):
    file = await input_file.read()
    if not os.path.exists(f"userspace/{current_user.username}"):
        os.mkdir(f"userspace/{current_user.username}")
        os.mkdir(f"userspace/{current_user.username}/tempfiles")
    user_space_path = "userspace/{current_user.username}"
    current_folder_path = f"userspace/{current_user.username}/tempfiles"
    stego_img, U_key, Vt_key, scale, S_key = joblib.load(io.BytesIO(file))
    print(stego_img.shape)
    ex_image =algorithm.extract(stego_img, U_key, Vt_key, scale, S_key)
    file_path = f"{current_folder_path}/output_message_{int(datetime.datetime.now().timestamp())}.jpg"
    cv2.imwrite(file_path,ex_image)
    return FileResponse(file_path,filename="message.png",background=BackgroundTask(clean_storage,file_path))


