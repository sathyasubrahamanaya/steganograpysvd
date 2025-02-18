from fastapi import Depends,APIRouter , BackgroundTasks,UploadFile
from app.core import text_encoding as te
import os
from app.security import get_current_user
from PIL import Image
import io
import datetime
from fastapi.responses import FileResponse
import time
from fastapi import Form
text_router = APIRouter()

def clean_files(filepaths):
   try:
     time.sleep(30)
     for file in filepaths:
        os.remove(file)
   except Exception as e:
      print(e)

@text_router.post("/encodeText")
async def encode_text(input_image:UploadFile,input_text:str = Form(...),current_user = Depends(get_current_user),background_task= BackgroundTasks()):
    if not os.path.exists(f"userspace/{current_user.username}"):
        os.mkdir(f"userspace/{current_user.username}")
        os.mkdir(f"userspace/{current_user.username}/tempfiles")
        
    user_space_path = "userspace/{current_user.username}"
    current_folder_path = f"userspace/{current_user.username}/tempfiles"
    file = await input_image.read()
    tmp_file_input_path = f"{current_folder_path}/text_hiding_input{datetime.datetime.now().timestamp()}.png"
    tmp_file_output_path = f"{current_folder_path}/text_hiding_output{datetime.datetime.now().timestamp()}.png"
    Image.open(io.BytesIO(file)).save(tmp_file_input_path)
    te.encode(tmp_file_input_path,input_text,tmp_file_output_path)
    background_task.add_task(clean_files,[tmp_file_input_path,tmp_file_output_path])
    return FileResponse(tmp_file_output_path,media_type="image/png",filename="download.png")


@text_router.post("/decodeText")
async def decode_text(input_image:UploadFile,current_user = Depends(get_current_user),background_task= BackgroundTasks()):
    if not os.path.exists(f"userspace/{current_user.username}"):
        os.mkdir(f"userspace/{current_user.username}")
        os.mkdir(f"userspace/{current_user.username}/tempfiles")
        
    user_space_path = "userspace/{current_user.username}"
    current_folder_path = f"userspace/{current_user.username}/tempfiles"
    file = await input_image.read()
    tmp_file_input_path = f"{current_folder_path}/text_hiding_input{datetime.datetime.now().timestamp()}.png"
    Image.open(io.BytesIO(file)).save(tmp_file_input_path)
    text_decoded = te.decode(tmp_file_input_path)
    background_task.add_task(clean_files,[tmp_file_input_path])
    return {"ErrorCode":0,"Message":"success","Data":{"decoded_text":text_decoded}}
    



    

