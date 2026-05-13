import os
import uuid
import streamlit as st

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from text_detector import detect_text_scam
from URL_Detector import detect_url_scam
from video_detector import analyze_video
from Image_Detector import analyze_image, get_ocr_status

st.title("TruthShield AI")
st.success("Streamlit is working!")

MAX_IMAGE_UPLOAD_MB = int(os.getenv("MAX_IMAGE_UPLOAD_MB", "40"))
MAX_VIDEO_UPLOAD_MB = int(os.getenv("MAX_VIDEO_UPLOAD_MB", "150"))
UPLOAD_CHUNK_SIZE = 1024 * 1024

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


def _save_upload(file, max_size_mb):
    safe_name = os.path.basename(file.filename or "upload")
    file_path = f"temp_{uuid.uuid4().hex}_{safe_name}"
    max_bytes = max_size_mb * 1024 * 1024
    total_bytes = 0

    try:
        with open(file_path, "wb") as buffer:
            while True:
                chunk = file.file.read(UPLOAD_CHUNK_SIZE)

                if not chunk:
                    break

                total_bytes += len(chunk)

                if total_bytes > max_bytes:
                    raise HTTPException(
                        status_code=413,
                        detail=f"File too large. Maximum allowed size is {max_size_mb} MB.",
                    )

                buffer.write(chunk)
    except Exception:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise

    return file_path


@app.post("/detect-video")
async def video_api(file: UploadFile = File(...)):
    file_path = _save_upload(file, MAX_VIDEO_UPLOAD_MB)
    result = analyze_video(file_path)
    return result

@app.post("/detect-image")
async def image_api(file: UploadFile = File(...)):
    file_path = _save_upload(file, MAX_IMAGE_UPLOAD_MB)
    result = analyze_image(file_path)
    return result

@app.get("/ocr-status")
async def ocr_status_api():
    return get_ocr_status()
