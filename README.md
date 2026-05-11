# hackindia-ai-deeptech-hackathon-abes-ghaziabad-cyber-sentinels
Hackathon team repository for Cyber Sentinels - [hackindia-team:hackindia-ai-deeptech-hackathon-abes-ghaziabad:cyber-sentinels]
# 🛡️ TruthShield AI

TruthShield AI is an AI-powered multimodal cybersecurity platform designed to detect phishing scams, fake screenshots, malicious URLs, OCR-based fraud content, and AI-generated/deepfake videos in real time.

Built for hackathons and cybersecurity awareness, the platform combines OCR, machine learning, computer vision, and AI-based frame analysis into one unified detection system.

---
# 🌐 Live Demo
https://truthshieldai-one.vercel.app/

# 🚀 Features

URL Scam Detection  
Screenshot & OCR Scam Detection  
AI-Generated / Deepfake Video Detection  
Real-time Risk Scoring  
Hybrid AI + Visual Inconsistency Analysis  
Modern Responsive UI  
Cloud Deployment Ready  

---

# 🧠 Detection Modules

## 1. URL Scanner
Detects:
- Suspicious domains
- Fake login links
- Phishing keywords
- Scam patterns

## 2. OCR Screenshot Analysis
Extracts text from screenshots and checks for:
- Urgent scam language
- Fake payment requests
- Crypto scams
- Impersonation attempts

## 3. AI / Deepfake Video Detection
Analyzes video frames using:
- AI frame classification
- Visual inconsistency detection
- Deepfake probability estimation

## 4. Risk Scoring Engine
Combines outputs from all detection systems to generate:
- Risk Score (0–100)
- Threat Level
- Red Flag Reports

---

# 🛠️ Tech Stack

## Frontend
- React.js
- Vite
- CSS3

## Backend
- FastAPI
- Python

## AI / ML
- Hugging Face Models
- OpenCV
- OCR
- NumPy
- Pillow

## Deployment
- Render (Backend)
- Vercel (Frontend)

---

# 📂 Project Structure

```bash
TruthShieldAI/
│
├── frontend/
│   ├── src/
│   ├── public/
│   └── package.json
│
├── backend/
│   ├── main.py
│   ├── video_detector.py
│   ├── ai_frame_detector.py
│   ├── Image_Detector.py
│   ├── requirements.txt
│   └── .env
│
└── README.md

# ⚙️ How to Run the Project

# 🖥️ Backend Setup

## Move to Backend Folder

```bash
cd backend
```

## Create Virtual Environment

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### Mac/Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

---

## Install Backend Dependencies

```bash
pip install -r requirements.txt
```

---

## Create Environment Variable File

Create a `.env` file inside the backend folder:

```env
HF_TOKEN=your_huggingface_token
```

---

## Run Backend Server

```bash
python -m uvicorn main:app --reload
```

Backend will start on:

```bash
http://127.0.0.1:8000
```

---

# 🌐 Frontend Setup

Open a new terminal.

## Move to Frontend Folder

```bash
cd frontend
```

---

## Install Frontend Dependencies

```bash
npm install
```

---

## Run Frontend

```bash
npm run dev
```

Frontend will start on:

```bash
http://localhost:5173
```

---

# 🚀 Deployment

## Frontend Deployment
- Vercel

## Backend Deployment
- Render

---

# 🔐 Environment Variables

| Variable | Description |
|----------|-------------|
| HF_TOKEN | Hugging Face API Token |
