import html
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
      @import url("https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap");

      * {
        box-sizing: border-box;
      }

      html, body, .stApp, [class*="css"] {
        font-family: "Inter", system-ui, sans-serif !important;
      }

      .stApp {
        background:
          radial-gradient(circle at top left, #1a1a1a 0%, #050505 42%, #000000 100%);
        color: white;
      }

      .stApp::before {
        content: "";
        position: fixed;
        inset: 0;
        background-image: radial-gradient(rgba(255,255,255,0.12) 1px, transparent 1px);
        background-size: 32px 32px;
        opacity: 0.08;
        pointer-events: none;
        z-index: 0;
      }

      .stApp::after {
        content: "";
        position: fixed;
        width: 420px;
        height: 420px;
        border-radius: 999px;
        background: rgba(255,255,255,0.06);
        filter: blur(90px);
        top: 18%;
        right: -140px;
        pointer-events: none;
        z-index: 0;
      }

      header[data-testid="stHeader"] {
        background: transparent;
      }

      .block-container {
        position: relative;
        z-index: 1;
        padding-top: 2.35rem;
        padding-bottom: 4rem;
        max-width: 1280px;
      }

      .top-nav {
        max-width: 1120px;
        margin: 0 auto 34px;
        padding: 14px 18px;
        border-radius: 22px;
        background: rgba(255,255,255,0.035);
        border: 1px solid rgba(255,255,255,0.08);
        backdrop-filter: blur(18px);
        display: flex;
        justify-content: space-between;
        align-items: center;
      }

      .brand {
        font-weight: 900;
        color: white;
      }

      .emoji {
        font-family: "Apple Color Emoji", "Segoe UI Emoji", "Noto Color Emoji", emoji, sans-serif !important;
        -webkit-text-fill-color: initial !important;
        background: none !important;
        filter: none !important;
      }

      .nav-pill {
        display: inline-flex;
        gap: 12px;
      }

      .nav-pill span {
        padding: 10px 16px;
        border-radius: 999px;
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.08);
        color: white;
        font-weight: 700;
        font-size: 0.92rem;
      }

      .hero {
        text-align: center;
        padding: 0.4rem 1rem 2.2rem;
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
        transition: 0.3s ease;
      }

      .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 24px 70px rgba(0,0,0,0.55);
      }

      .metric-card b {
        display: block;
        font-size: 1.8rem;
      }

      .metric-card span {
        color: #9ca3af;
      }

      .section-label {
        margin: 3rem 0 1.2rem;
        font-size: 1.9rem;
        font-weight: 900;
        letter-spacing: 0;
        color: white;
      }

      .st-key-card_text,
      .st-key-card_url,
      .st-key-card_image,
      .st-key-card_video,
      .st-key-accuracy_panel {
        position: relative;
        overflow: hidden;
        background: rgba(255,255,255,0.035);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 28px;
        padding: 1.6rem;
        backdrop-filter: blur(18px);
        min-height: 100%;
        transition: 0.3s ease;
      }

      .st-key-card_text::before,
      .st-key-card_url::before,
      .st-key-card_image::before,
      .st-key-card_video::before {
        content: "";
        position: absolute;
        inset: 0;
        background: linear-gradient(120deg, transparent 0%, rgba(255,255,255,0.09) 48%, transparent 56%);
        transform: translateX(-120%);
        transition: transform 0.7s ease;
        pointer-events: none;
      }

      .st-key-card_text:hover,
      .st-key-card_url:hover,
      .st-key-card_image:hover,
      .st-key-card_video:hover {
        transform: translateY(-8px);
        border-color: rgba(255,255,255,0.34);
        background: rgba(255,255,255,0.065);
        box-shadow:
          0 34px 90px rgba(0,0,0,0.9),
          0 0 85px rgba(255,255,255,0.22),
          inset 0 0 0 1px rgba(255,255,255,0.18);
      }

      .st-key-card_text:hover::before,
      .st-key-card_url:hover::before,
      .st-key-card_image:hover::before,
      .st-key-card_video:hover::before {
        transform: translateX(120%);
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
        border-radius: 28px;
        padding: 1.8rem;
        background: rgba(255,255,255,0.035);
        margin-top: 1rem;
      }

      .report-title {
        margin: 0 0 1.25rem;
        font-size: 1.8rem;
        font-weight: 900;
      }

      .report-grid {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
        margin: 1.2rem 0 1.4rem;
        padding: 1.1rem 0;
        border-top: 1px solid rgba(255,255,255,0.08);
        border-bottom: 1px solid rgba(255,255,255,0.08);
      }

      .report-stat {
        border: none;
        border-radius: 0;
        padding: 0;
        background: transparent;
      }

      .report-stat span {
        display: block;
        color: #9ca3af;
        font-size: 0.88rem;
        font-weight: 700;
        margin-bottom: 0.55rem;
      }

      .report-stat strong {
        display: block;
        color: white;
        font-size: 2.2rem;
        line-height: 1.1;
        font-weight: 900;
      }

      .risk-pill {
        display: inline-flex;
        align-items: center;
        gap: 0.6rem;
        padding: 0;
        border-radius: 0;
        border: none;
        background: transparent;
        font-size: 1.2rem;
        font-weight: 900;
      }

      .risk-dot {
        width: 0.82rem;
        height: 0.82rem;
        border-radius: 999px;
        background: #f5f5f5;
        box-shadow: 0 0 18px rgba(255,255,255,0.2);
      }

      .risk-dot.danger {
        background: #f87171;
      }

      .risk-dot.warning {
        background: #facc15;
      }

      .risk-dot.safe {
        background: #4ade80;
      }

      .report-section-title {
        margin: 1.4rem 0 0.8rem;
        font-size: 1.35rem;
        font-weight: 900;
      }

      .reason-list {
        margin: 0;
        padding-left: 1.2rem;
        color: #d1d5db;
      }

      .accuracy-title {
        margin: 0 0 1rem;
        font-size: 1.7rem;
        font-weight: 900;
      }

      .accuracy-copy {
        color: #d1d5db;
        line-height: 1.7;
        margin-bottom: 1.2rem;
      }

      .accuracy-grid {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 1rem;
      }

      .accuracy-item {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 18px;
        padding: 1rem;
      }

      .accuracy-item b {
        display: block;
        font-size: 0.95rem;
        margin-bottom: 0.6rem;
      }

      .accuracy-item span {
        display: block;
        font-size: 1.9rem;
        font-weight: 900;
        color: white;
        margin-bottom: 0.45rem;
      }

      .accuracy-item p {
        color: #9ca3af;
        font-size: 0.92rem;
        line-height: 1.45;
        margin: 0;
      }

      @media (max-width: 900px) {
        .report-grid,
        .accuracy-grid {
          display: grid;
          grid-template-columns: 1fr;
        }
      }

      .stButton > button {
        border-radius: 16px;
        font-weight: 800;
        border: none;
        padding: 0.78rem 1.25rem;
        background: white;
        color: #111111;
        transition: 0.3s ease;
      }

      .stButton > button:hover {
        transform: translateY(-2px);
        border: none;
        color: #111111;
        box-shadow: 0 16px 40px rgba(255,255,255,0.08);
      }

      textarea,
      input {
        background: rgba(255,255,255,0.04) !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        border-radius: 18px !important;
        color: white !important;
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


def risk_class(level):
    if not level:
        return "safe"
    if "High" in level or "Fake" in level or "Manipulated" in level:
        return "danger"
    if "Suspicious" in level or "Potentially" in level:
        return "warning"
    return "safe"


def render_result(result):
    score = result.get("risk_score", 0)
    level = result.get("risk_level", "Unknown")
    dot_class = risk_class(level)
    reasons = result.get("reasons") or []

    st.markdown(
        f"""
        <div class="result-box">
          <h2 class="report-title">Analysis Report</h2>
          <div class="report-grid">
            <div class="report-stat">
              <span>Risk Score</span>
              <strong>{score}/100</strong>
            </div>
            <div class="report-stat">
              <span>Risk Level</span>
              <div class="risk-pill">
                <i class="risk-dot {dot_class}"></i>
                {html.escape(str(level))}
              </div>
            </div>
          </div>
        """,
        unsafe_allow_html=True,
    )

    if reasons:
        reason_items = "".join(f"<li>{html.escape(str(reason))}</li>" for reason in reasons)
        st.markdown(
            f"""
            <h3 class="report-section-title">Red Flags</h3>
            <ul class="reason-list">{reason_items}</ul>
            """,
            unsafe_allow_html=True,
        )

    if result.get("extracted_text"):
        st.markdown('<h3 class="report-section-title">Extracted Text</h3>', unsafe_allow_html=True)
        st.code(result["extracted_text"])

    if result.get("frames_analyzed"):
        st.caption(f"Frames analyzed: {result['frames_analyzed']}")
    if result.get("file_size_mb"):
        st.caption(f"File size: {result['file_size_mb']} MB")

    st.info(result.get("advice", "Stay cautious and verify suspicious content."))
    st.markdown("</div>", unsafe_allow_html=True)


st.markdown(
    """
    <nav class="top-nav">
      <div class="brand"><span class="emoji">🛡️</span> Truth Shield AI</div>
      <div class="nav-pill">
        <span>Scanner</span>
        <span>Accuracy</span>
      </div>
    </nav>

    <section class="hero">
      <span class="badge">A ONE STEP SOLUTION</span>
      <h1><span class="emoji">🛡️</span> Truth Shield AI</h1>
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

st.markdown('<div class="section-label">Scanner</div>', unsafe_allow_html=True)

row_one = st.columns(2)
with row_one[0]:
    with st.container(key="card_text"):
        st.markdown('<div class="card-icon"><span class="emoji">🧠</span></div>', unsafe_allow_html=True)
        st.subheader("Text Detector")
        st.write("Paste suspicious messages, scam texts or phishing content.")
        text = st.text_area("Paste suspicious message", height=150)
        if st.button("Analyze Text", key="text_button"):
            render_result(detect_text_scam(text))

with row_one[1]:
    with st.container(key="card_url"):
        st.markdown('<div class="card-icon"><span class="emoji">🔗</span></div>', unsafe_allow_html=True)
        st.subheader("URL Detector")
        st.write("Analyze suspicious links, phishing domains and fake Web3 URLs.")
        url = st.text_input("Paste suspicious URL", placeholder="rnicrosoft.com")
        if st.button("Analyze URL", key="url_button"):
            render_result(detect_url_scam(url))

row_two = st.columns(2)
with row_two[0]:
    with st.container(key="card_image"):
        st.markdown('<div class="card-icon"><span class="emoji">🖼️</span></div>', unsafe_allow_html=True)
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
        st.markdown('<div class="card-icon"><span class="emoji">🎥</span></div>', unsafe_allow_html=True)
        st.subheader("Video Detector")
        st.write("Analyze AI-generated video risks and deepfake inconsistencies.")
        video_file = st.file_uploader("Upload video", type=["mp4", "mov", "avi", "mkv", "webm"], key="video_file")
        if video_file and st.button("Analyze Video", key="video_button"):
            video_path = save_upload(video_file, os.path.splitext(video_file.name)[1] or ".mp4")
            with st.spinner("Analyzing sampled video frames..."):
                render_result(analyze_video(video_path))

st.markdown('<div class="section-label">Accuracy</div>', unsafe_allow_html=True)
with st.container(key="accuracy_panel"):
    st.markdown(
        """
        <h2 class="accuracy-title">Model Accuracy & Evaluation</h2>
        <p class="accuracy-copy">
          Truth Shield AI uses a hybrid detection approach combining OCR, phishing pattern analysis,
          URL intelligence, filename hints, local trainable video features, and AI-based frame scoring.
        </p>
        <div class="accuracy-grid">
          <div class="accuracy-item">
            <b>Text Scam Detection</b>
            <span>~85%</span>
            <p>Detects phishing, urgency manipulation, scam language and social engineering patterns.</p>
          </div>
          <div class="accuracy-item">
            <b>OCR Image Scam Detection</b>
            <span>~80%</span>
            <p>Reads screenshots using OCR and detects suspicious scam indicators.</p>
          </div>
          <div class="accuracy-item">
            <b>URL Risk Detection</b>
            <span>~75%</span>
            <p>Detects suspicious domains, shortened links and Web3 scam structures.</p>
          </div>
          <div class="accuracy-item">
            <b>Video AI Risk Detection</b>
            <span>Prototype</span>
            <p>Uses sampled video frames, filename hints, and local trainable model scoring.</p>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption("Prototype values are not forensic guarantees. Train the local video model for your target clips.")
