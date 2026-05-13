import streamlit as st

st.set_page_config(page_title="TruthShield AI", layout="centered")

st.title("🛡️ TruthShield AI")
st.subheader("AI-Powered Scam & Phishing Detector")

st.success("Streamlit deployment is working!")

uploaded_file = st.file_uploader(
    "Upload a suspicious screenshot",
    type=["png", "jpg", "jpeg"]
)

if uploaded_file:
    st.image(uploaded_file, caption="Uploaded Image", use_container_width=True)
    st.warning("OCR detector integration coming next...")