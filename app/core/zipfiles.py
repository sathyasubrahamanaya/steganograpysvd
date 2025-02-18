import os
import zipfile
import io
from fastapi.responses import StreamingResponse,FileResponse
import datetime

def return_zipfile(files:list,current_folder:str,):
    zip_path = f"{current_folder}/zippy_{int(datetime.datetime.now().timestamp())}.zip"
    with zipfile.ZipFile(zip_path, 'w') as zipMe:
         for file in files:
            zipMe.write(file,compress_type=zipfile.ZIP_DEFLATED)
   
    
    return FileResponse(zip_path,media_type="application/zip",
                        filename="outputs.zip",
                        )