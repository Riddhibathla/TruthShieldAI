from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from text_detector import detect_text_scam
from URL_Detector import detect_url_scam
from video_detector import analyze_video
from Image_Detector import analyze_image
import shutil

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/detect-text")
async def text_api(data: dict):
    return detect_text_scam(data["text"])

@app.post("/detect-url")
async def url_api(data: dict):
    return detect_url_scam(data["url"])

@app.post("/detect-video")
async def video_api(file: UploadFile = File(...)):
    file_path = f"temp_{file.filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    result = analyze_video(file_path)
    return result

@app.post("/detect-image")
async def image_api(file: UploadFile = File(...)):
    file_path = f"temp_{file.filename}"

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    result = analyze_image(file_path)
    return result