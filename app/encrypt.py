from fastapi import APIRouter, Depends, HTTPException, status, UploadFile
from PIL import Image
import datetime
import io
from .core import algorithm,zipfiles
import zipfile
import os
import cv2
import joblib
from app.models import User
from app.security import get_current_user
from fastapi.background import BackgroundTasks
import shutil
import time
encrpyt_router = APIRouter()

def clean_up(folder):
    try:
        time.sleep(300)
        print("cleaning up ---------->",folder)
        for file in os.listdir(folder):
            os.remove(f"{folder}/{file}")
    except Exception as e:
        print(e)

def convert_png(uploaded_image_bytes,sub_name="input",save_in_path:str="tempfiles"):
    image =Image.open(io.BytesIO(uploaded_image_bytes))
    image_path_str = f"{save_in_path}/image_{sub_name}{datetime.datetime.now().timestamp()}.png"
    image.save(image_path_str)
    return image_path_str

@encrpyt_router.get("/encrypt")
async def encrpyt_images(input_image:UploadFile,cover_image:UploadFile,current_user:User = Depends(get_current_user),backgroud_tasks: BackgroundTasks= BackgroundTasks() ):
    if not os.path.exists(f"userspace/{current_user.username}"):
        os.mkdir(f"userspace/{current_user.username}")
        os.mkdir(f"userspace/{current_user.username}/tempfiles")
        
    user_space_path = "userspace/{current_user.username}"
    current_folder_path = f"userspace/{current_user.username}/tempfiles"
    input_image_path =convert_png(await input_image.read(),save_in_path=current_folder_path) #lossless image compression
    output_image_path = convert_png(await cover_image.read(),sub_name="output",save_in_path= current_folder_path)
    stego_img, U_key, Vt_key, scale, S_key  = algorithm.embed(output_image_path,input_image_path,scale_factor=1)
    output_stego_path = f"{current_folder_path}/stego_{datetime.datetime.now().timestamp()}.png"
    output_key_path = f"{current_folder_path}/key_{datetime.datetime.now().timestamp()}.joblib"
    joblib.dump([stego_img,U_key,Vt_key,scale,S_key],output_key_path)
    cv2.imwrite(output_stego_path,stego_img)
    backgroud_tasks.add_task(clean_up,current_folder_path)
    return zipfiles.return_zipfile([output_stego_path,output_key_path],current_folder_path)
    
    


    



