# app/main.py
from fastapi import FastAPI
from sqlmodel import SQLModel
from app.database import engine
from app.auth import router as auth_router
from app.encrypt import encrpyt_router
from app.decrypt import decrpyt_router
from app.text_encoder import text_router
import os
import shutil



app = FastAPI()

@app.on_event("startup")
def on_startup():
    
    if not os.path.exists("userspace"):
        os.mkdir("userspace")
    else:
        shutil.rmtree("userspace")
        os.mkdir("userspace")

        
       
    SQLModel.metadata.create_all(engine)

app.include_router(auth_router)
app.include_router(encrpyt_router)
app.include_router(decrpyt_router)
app.include_router(text_router)
