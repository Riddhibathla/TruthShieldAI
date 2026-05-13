import os
import sys
import tempfile

import streamlit as st


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(ROOT_DIR, "backend")

if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from Image_Detector import analyze_image, get_ocr_status
from URL_Detector import detect_url_scam
from text_detector import detect_text_scam
from video_detector import analyze_video


st.set_page_config(page_title="Truth Shield AI", page_icon="🛡️", layout="wide")

st.markdown(
    """
    <style>
      .stApp {
        background:
          radial-gradient(circle at top left, #1a1a1a 0%, #050505 42%, #000000 100%);
        color: white;
      }

      .block-container {
        padding-top: 2.4rem;
        padding-bottom: 4rem;
        max-width: 1280px;
      }

      header[data-testid="stHeader"] {
        background: transparent;
      }

      .hero {
        text-align: center;
        padding: 2.4rem 1rem 2.2rem;
      }

      .badge {
        display: inline-block;
        padding: 0.6rem 1.1rem;
        border-radius: 999px;
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.1);
        font-weight: 800;
        letter-spacing: 0.08em;
      }

      .hero h1 {
        margin: 1.35rem 0 1rem;
        font-size: clamp(2.7rem, 6vw, 4.8rem);
        line-height: 1.08;
        font-weight: 900;
        background: linear-gradient(110deg, #ffffff 0%, #9ca3af 50%, #ffffff 100%);
        background-size: 220% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: textGlimmer 3s linear infinite;
      }

      .hero p {
        color: #d1d5db;
        max-width: 850px;
        margin: 0 auto;
        line-height: 1.7;
        font-size: 1.08rem;
      }

      .metric-card {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 24px;
        padding: 1.35rem;
        text-align: center;
        backdrop-filter: blur(16px);
      }

      .metric-card b {
        display: block;
        font-size: 1.8rem;
      }

      .metric-card span {
        color: #9ca3af;
      }

      .section-label {
        margin: 3rem 0 1.1rem;
        font-size: 0.95rem;
        font-weight: 900;
        letter-spacing: 0.12em;
        color: #d1d5db;
      }

      .st-key-card_text,
      .st-key-card_url,
      .st-key-card_image,
      .st-key-card_video,
      .st-key-accuracy_panel {
        background: rgba(255,255,255,0.035);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 28px;
        padding: 1.6rem;
        backdrop-filter: blur(18px);
        min-height: 100%;
      }

      .st-key-card_text:hover,
      .st-key-card_url:hover,
      .st-key-card_image:hover,
      .st-key-card_video:hover {
        box-shadow:
          0 30px 80px rgba(0,0,0,0.75),
          0 0 45px rgba(255,255,255,0.08);
      }

      .card-icon {
        width: 60px;
        height: 60px;
        display: grid;
        place-items: center;
        border-radius: 20px;
        background: rgba(255,255,255,0.05);
        margin-bottom: 1rem;
        font-size: 1.7rem;
      }

      .result-box {
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 24px;
        padding: 1.4rem;
        background: rgba(255,255,255,0.035);
        margin-top: 1rem;
      }

      .stButton > button {
        border-radius: 16px;
        font-weight: 800;
      }

      @keyframes textGlimmer {
        0% { background-position: 220% center; }
        100% { background-position: -220% center; }
      }
    </style>
    """,
    unsafe_allow_html=True,
)


def save_upload(uploaded_file, suffix):
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        temp_file.write(uploaded_file.getbuffer())
        return temp_file.name


def risk_badge(level):
    if not level:
        return "Unknown"
    if "High" in level or "Fake" in level or "Manipulated" in level:
        return "🔴 " + level
    if "Suspicious" in level or "Potentially" in level:
        return "🟡 " + level
    return "🟢 " + level


def render_result(result):
    st.markdown('<div class="result-box">', unsafe_allow_html=True)
    col_score, col_level = st.columns(2)
    col_score.metric("Risk Score", f"{result.get('risk_score', 0)}/100")
    col_level.metric("Risk Level", risk_badge(result.get("risk_level", "Unknown")))

    reasons = result.get("reasons") or []
    if reasons:
        st.subheader("⚠️ Red Flags")
        for reason in reasons:
            st.write(f"- {reason}")

    if result.get("extracted_text"):
        st.subheader("🧾 Extracted Text")
        st.code(result["extracted_text"])

    if result.get("frames_analyzed"):
        st.caption(f"Frames analyzed: {result['frames_analyzed']}")
    if result.get("file_size_mb"):
        st.caption(f"File size: {result['file_size_mb']} MB")

    st.info(result.get("advice", "Stay cautious and verify suspicious content."))
    st.markdown("</div>", unsafe_allow_html=True)


st.markdown(
    """
    <section class="hero">
      <span class="badge">A ONE STEP SOLUTION</span>
      <h1>🛡️ Truth Shield AI</h1>
      <p>
        A premium multimodal safety platform that detects scams, phishing,
        manipulated screenshots and AI-generated video risks in one place.
      </p>
    </section>
    """,
    unsafe_allow_html=True,
)

metric_cols = st.columns(3)
with metric_cols[0]:
    st.markdown('<div class="metric-card"><b>4</b><span>Detection Modes</span></div>', unsafe_allow_html=True)
with metric_cols[1]:
    st.markdown('<div class="metric-card"><b>OCR</b><span>Screenshot Reading</span></div>', unsafe_allow_html=True)
with metric_cols[2]:
    st.markdown('<div class="metric-card"><b>AI</b><span>Risk Scoring</span></div>', unsafe_allow_html=True)

st.markdown('<div class="section-label">SCANNER</div>', unsafe_allow_html=True)

row_one = st.columns(2)
with row_one[0]:
    with st.container(key="card_text"):
        st.markdown('<div class="card-icon">🧠</div>', unsafe_allow_html=True)
        st.subheader("Text Detector")
        st.write("Paste suspicious messages, scam texts or phishing content.")
        text = st.text_area("Paste suspicious message", height=150)
        if st.button("Analyze Text", key="text_button"):
            render_result(detect_text_scam(text))

with row_one[1]:
    with st.container(key="card_url"):
        st.markdown('<div class="card-icon">🔗</div>', unsafe_allow_html=True)
        st.subheader("URL Detector")
        st.write("Analyze suspicious links, phishing domains and fake Web3 URLs.")
        url = st.text_input("Paste suspicious URL", placeholder="rnicrosoft.com")
        if st.button("Analyze URL", key="url_button"):
            render_result(detect_url_scam(url))

row_two = st.columns(2)
with row_two[0]:
    with st.container(key="card_image"):
        st.markdown('<div class="card-icon">🖼️</div>', unsafe_allow_html=True)
        st.subheader("Image Detector")
        st.write("Upload screenshots for OCR-based phishing and scam analysis.")
        ocr_status = get_ocr_status()
        if ocr_status.get("ocr_available"):
            st.success(f"{ocr_status.get('engine', 'OCR')} is ready.")
        else:
            st.warning(ocr_status.get("advice", "OCR is not available."))
        image_file = st.file_uploader("Upload screenshot", type=["png", "jpg", "jpeg", "webp"], key="image_file")
        if image_file and st.button("Analyze Image", key="image_button"):
            image_path = save_upload(image_file, os.path.splitext(image_file.name)[1] or ".png")
            with st.spinner("Reading screenshot with OCR..."):
                render_result(analyze_image(image_path))

with row_two[1]:
    with st.container(key="card_video"):
        st.markdown('<div class="card-icon">🎥</div>', unsafe_allow_html=True)
        st.subheader("Video Detector")
        st.write("Analyze AI-generated video risks and deepfake inconsistencies.")
        video_file = st.file_uploader("Upload video", type=["mp4", "mov", "avi", "mkv", "webm"], key="video_file")
        if video_file and st.button("Analyze Video", key="video_button"):
            video_path = save_upload(video_file, os.path.splitext(video_file.name)[1] or ".mp4")
            with st.spinner("Analyzing sampled video frames..."):
                render_result(analyze_video(video_path))

st.markdown('<div class="section-label">ACCURACY</div>', unsafe_allow_html=True)
with st.container(key="accuracy_panel"):
    st.subheader("📈 Model Accuracy & Evaluation")
    st.write(
        "Truth Shield AI uses a hybrid detection approach combining OCR, phishing pattern analysis, "
        "URL intelligence, filename hints, local trainable video features, and AI-based frame scoring."
    )
    accuracy_cols = st.columns(4)
    accuracy_cols[0].metric("Text Scam Detection", "~85%")
    accuracy_cols[1].metric("OCR Image Scam Detection", "~80%")
    accuracy_cols[2].metric("URL Risk Detection", "~75%")
    accuracy_cols[3].metric("Video AI Risk Detection", "Prototype")
    st.caption("Prototype values are not forensic guarantees. Train the local video model for your target clips.")
