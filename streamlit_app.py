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


st.set_page_config(
    page_title="Truth Shield AI",
    page_icon="🛡️",
    layout="wide",
)


st.markdown(
    """
    <style>
      .stApp {
        background:
          radial-gradient(circle at top left, #1a1a1a 0%, #050505 42%, #000000 100%);
        color: white;
      }

      .block-container {
        padding-top: 2.5rem;
        padding-bottom: 4rem;
        max-width: 1180px;
      }

      .hero {
        text-align: center;
        padding: 2.8rem 1rem 2.2rem;
      }

      .badge {
        display: inline-block;
        padding: 0.55rem 1rem;
        border: 1px solid rgba(255,255,255,0.12);
        border-radius: 999px;
        background: rgba(255,255,255,0.05);
        color: #f5f5f5;
        font-weight: 800;
        font-size: 0.78rem;
        letter-spacing: 0.08em;
      }

      .hero h1 {
        margin: 1.25rem 0 0.85rem;
        font-size: clamp(2.7rem, 6vw, 4.6rem);
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
        max-width: 820px;
        margin: 0 auto;
        line-height: 1.7;
        font-size: 1.08rem;
      }

      .metric-card {
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 24px;
        padding: 1.15rem;
        background: rgba(255,255,255,0.035);
        text-align: center;
      }

      .metric-card b {
        display: block;
        font-size: 1.8rem;
      }

      .metric-card span {
        color: #9ca3af;
      }

      .result-box {
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 24px;
        padding: 1.4rem;
        background: rgba(255,255,255,0.035);
        margin-top: 1rem;
      }

      @keyframes textGlimmer {
        0% { background-position: 220% center; }
        100% { background-position: -220% center; }
      }

      div[data-testid="stTabs"] button {
        color: white;
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

st.divider()

tabs = st.tabs(["🧠 Text", "🔗 URL", "🖼️ Image OCR", "🎥 Video AI", "📈 Accuracy"])

with tabs[0]:
    st.subheader("Text Detector")
    text = st.text_area("Paste suspicious message", height=170)

    if st.button("Analyze Text", key="text_button"):
        render_result(detect_text_scam(text))

with tabs[1]:
    st.subheader("URL Detector")
    url = st.text_input("Paste suspicious URL", placeholder="rnicrosoft.com")

    if st.button("Analyze URL", key="url_button"):
        render_result(detect_url_scam(url))

with tabs[2]:
    st.subheader("Image Detector")
    ocr_status = get_ocr_status()

    if ocr_status.get("ocr_available"):
        st.success(f"{ocr_status.get('engine', 'OCR')} is ready.")
    else:
        st.warning(ocr_status.get("advice", "OCR is not available."))

    image_file = st.file_uploader(
        "Upload screenshot",
        type=["png", "jpg", "jpeg", "webp"],
        key="image_file",
    )

    if image_file and st.button("Analyze Image", key="image_button"):
        suffix = os.path.splitext(image_file.name)[1] or ".png"
        image_path = save_upload(image_file, suffix)

        with st.spinner("Reading screenshot with OCR..."):
            render_result(analyze_image(image_path))

with tabs[3]:
    st.subheader("Video Detector")
    st.caption("For Streamlit Cloud, keep uploads compact for faster analysis.")

    video_file = st.file_uploader(
        "Upload video",
        type=["mp4", "mov", "avi", "mkv", "webm"],
        key="video_file",
    )

    if video_file and st.button("Analyze Video", key="video_button"):
        suffix = os.path.splitext(video_file.name)[1] or ".mp4"
        video_path = save_upload(video_file, suffix)

        with st.spinner("Analyzing sampled video frames..."):
            render_result(analyze_video(video_path))

with tabs[4]:
    st.subheader("Model Accuracy & Evaluation")
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
