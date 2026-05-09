import { useState } from "react";
import axios from "axios";
import "./App.css";

function App() {
  const [text, setText] = useState("");
  const [url, setUrl] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const API = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

  const handleRequest = async (requestFn) => {
    setLoading(true);
    setResult(null);

    try {
      const res = await requestFn();
      setResult(res.data);
    } catch (err) {
      console.error(err);
      alert("Backend error. Make sure FastAPI is running.");
    }

    setLoading(false);
  };

  const checkText = () =>
    handleRequest(() =>
      axios.post(`${API}/detect-text`, { text })
    );

  const checkUrl = () =>
    handleRequest(() =>
      axios.post(`${API}/detect-url`, { url })
    );

  const checkImage = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    handleRequest(() =>
      axios.post(`${API}/detect-image`, formData)
    );
  };

  const checkVideo = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    handleRequest(() =>
      axios.post(`${API}/detect-video`, formData)
    );
  };

  const scrollToScanner = () => {
    document
      .getElementById("scanner")
      .scrollIntoView({ behavior: "smooth" });
  };

  const scrollToAccuracy = () => {
    document
      .getElementById("accuracy")
      .scrollIntoView({ behavior: "smooth" });
  };

  return (
    <div className="app">

      {/* NAVBAR */}
      <nav className="navbar">

        <div className="brand">
          🛡️ Truth Shield AI
        </div>

        <div className="navLinks">

          <button
            className="navBtn"
            onClick={scrollToScanner}
          >
            Scanner
          </button>

          <button
            className="navBtn"
            onClick={scrollToAccuracy}
          >
            Accuracy
          </button>

        </div>

      </nav>

      {/* HERO */}
      <section className="hero">

        <p className="badge">
          A ONE STEP SOLUTION
        </p>

        <h1>Truth Shield AI</h1>

        <p className="heroText">
          A premium multimodal safety platform that detects scams,
          phishing, manipulated screenshots and AI-generated
          video risks in one place.
        </p>

        <div className="heroActions">

          <button onClick={scrollToScanner}>
            Start Scanning
          </button>

          <button
            className="secondaryBtn"
            onClick={scrollToScanner}
          >
            View Demo
          </button>

        </div>

        <div className="stats">

          <div>
            <b>4</b>
            <span>Detection Modes</span>
          </div>

          <div>
            <b>OCR</b>
            <span>Screenshot Reading</span>
          </div>

          <div>
            <b>AI</b>
            <span>Risk Scoring</span>
          </div>

        </div>

      </section>

      {/* SCANNER */}
      <section className="grid" id="scanner">

        {/* TEXT */}
        <div className="card">

          <div className="icon">🧠</div>

          <h2>Text Detector</h2>

          <p>
            Paste suspicious messages,
            scam texts or phishing content.
          </p>

          <textarea
            placeholder="Paste suspicious message..."
            value={text}
            onChange={(e) => setText(e.target.value)}
          />

          <button onClick={checkText}>
            Analyze Text
          </button>

        </div>

        {/* URL */}
        <div className="card">

          <div className="icon">🔗</div>

          <h2>URL Detector</h2>

          <p>
            Analyze suspicious links,
            phishing domains and fake Web3 URLs.
          </p>

          <input
            type="text"
            placeholder="Paste suspicious URL..."
            value={url}
            onChange={(e) => setUrl(e.target.value)}
          />

          <button onClick={checkUrl}>
            Analyze URL
          </button>

        </div>

        {/* IMAGE */}
        <div className="card">

          <div className="icon">🖼️</div>

          <h2>Image Detector</h2>

          <p>
            Upload screenshots for OCR-based
            phishing and scam analysis.
          </p>

          <input
            type="file"
            accept="image/*"
            onChange={checkImage}
          />

        </div>

        {/* VIDEO */}
        <div className="card">

          <div className="icon">🎥</div>

          <h2>Video Detector</h2>

          <p>
            Analyze AI-generated video risks
            and deepfake inconsistencies.
          </p>

          <input
            type="file"
            accept="video/*"
            onChange={checkVideo}
          />

        </div>

      </section>

      {/* LOADER */}
      {loading && (
        <div className="loader">

          <div className="spinner"></div>

          <span>
            Analyzing threat signals...
          </span>

        </div>
      )}

      {/* RESULT */}
      {result && (
        <section className="result">

          <h2>📊 Analysis Report</h2>

          <div className="scoreBox">

            <span>Risk Score</span>

            <strong>
              {result.risk_score}/100
            </strong>

          </div>

          <p>
            <b>Risk Level:</b>{" "}

            <span
              className={`level ${getClass(result.risk_level)}`}
            >
              {result.risk_level}
            </span>
          </p>

          {result.reasons && (
            <>

              <h3>⚠️ Red Flags</h3>

              <ul>
                {result.reasons.map((r, i) => (
                  <li key={i}>{r}</li>
                ))}
              </ul>

            </>
          )}

          {result.extracted_text && (
            <>

              <h3>🧾 Extracted Text</h3>

              <div className="ocrBox">
                {result.extracted_text}
              </div>

            </>
          )}

          <p className="advice">
            <b>Safety Advice:</b> {result.advice}
          </p>

        </section>
      )}

      {/* ACCURACY SECTION */}
      <section className="accuracy" id="accuracy">

        <h2>
          📈 Model Accuracy & Evaluation
        </h2>

        <p>
          Truth Shield AI uses a hybrid detection approach
          combining OCR, phishing pattern analysis,
          URL intelligence and AI-based visual risk scoring.
        </p>

        <div className="accuracyGrid">

          <div>

            <b>Text Scam Detection</b>

            <span>~85%</span>

            <p>
              Detects phishing, urgency manipulation,
              scam language and social engineering patterns.
            </p>

          </div>

          <div>

            <b>OCR Image Scam Detection</b>

            <span>~80%</span>

            <p>
              Reads screenshots using OCR
              and detects suspicious scam indicators.
            </p>

          </div>

          <div>

            <b>URL Risk Detection</b>

            <span>~75%</span>

            <p>
              Detects suspicious domains,
              shortened links and Web3 scam structures.
            </p>

          </div>

          <div>

            <b>Video AI Risk Detection</b>

            <span>Prototype</span>

            <p>
              Uses sampled video frames,
              AI scoring and visual inconsistency checks.
            </p>

          </div>

        </div>

        <p className="note">
          Note: These values represent prototype-level testing
          and are not forensic guarantees.
        </p>

      </section>

    </div>
  );
}

function getClass(level = "") {

  if (
    level.includes("High") ||
    level.includes("Fake") ||
    level.includes("Manipulated")
  ) {
    return "danger";
  }

  if (
    level.includes("Suspicious") ||
    level.includes("Potentially")
  ) {
    return "warning";
  }

  return "safe";
}

export default App;