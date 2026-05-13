import os

import cv2

from ai_frame_detector import check_frame_with_ai
from local_video_model import predict_with_local_model

MAX_AI_FRAMES = int(os.getenv("VIDEO_MAX_AI_FRAMES", "5"))
FAST_VIDEO_MB = int(os.getenv("FAST_VIDEO_MB", "25"))
FAST_VIDEO_AI_FRAMES = int(os.getenv("FAST_VIDEO_AI_FRAMES", "3"))
FRAME_JPEG_QUALITY = int(os.getenv("VIDEO_FRAME_JPEG_QUALITY", "82"))
FAKE_RECALL_THRESHOLD = int(os.getenv("VIDEO_FAKE_RECALL_THRESHOLD", "10"))
FAKE_SUSPICIOUS_THRESHOLD = int(os.getenv("VIDEO_FAKE_SUSPICIOUS_THRESHOLD", "25"))
FAKE_HIGH_THRESHOLD = int(os.getenv("VIDEO_FAKE_HIGH_THRESHOLD", "45"))
SUSPICIOUS_FILENAME_TERMS = {
    "ai": 52,
    "aivideo": 60,
    "generated": 58,
    "synthetic": 58,
    "deepfake": 70,
    "heygen": 70,
    "synthesia": 70,
    "did": 58,
    "d-id": 70,
    "pixverse": 70,
    "runway": 62,
    "pika": 62,
    "kling": 62,
    "sora": 62,
    "veo": 58,
}


def _cleanup(path):
    if path and os.path.exists(path):
        os.remove(path)


def _cleanup_frame(path):
    if path and os.path.exists(path):
        os.remove(path)


def _sample_frame_indexes(total_frames, fps, max_ai_frames):
    if total_frames and total_frames > 0:
        if max_ai_frames == 1:
            return [max(1, total_frames // 2)]

        start = max(1, int((fps or 30) * 0.5))
        end = max(start + 1, total_frames - 2)

        if max_ai_frames == 2:
            return [start, end]

        step = max(1, (end - start) // (max_ai_frames - 1))
        return sorted({min(end, start + (i * step)) for i in range(max_ai_frames)})

    interval = max(30, int((fps or 30) * 1.5))
    return [interval * (i + 1) for i in range(max_ai_frames)]


def _filename_risk(path):
    filename = os.path.basename(path).lower()
    normalized = filename.replace("_", "-").replace(" ", "-")
    hits = []
    score = 0

    for term, term_score in SUSPICIOUS_FILENAME_TERMS.items():
        if term in normalized:
            hits.append(term)
            score = max(score, term_score)

    return score, hits


def analyze_video(path):
    cap = cv2.VideoCapture(path)

    analyzed_frames = 0
    fake_scores = []
    real_scores = []
    suspicious_points = 0
    ai_statuses = []
    reasons = []

    os.makedirs("sampled_frames", exist_ok=True)
    file_size_mb = os.path.getsize(path) / (1024 * 1024) if os.path.exists(path) else 0
    filename_score, filename_hits = _filename_risk(path)
    if filename_hits:
        suspicious_points += filename_score
        reasons.append(
            f"Filename contains AI-generation signal: {', '.join(filename_hits)}"
        )

    local_result = predict_with_local_model(path)

    if local_result["status"] == "ok":
        fake_score = local_result["fake_score"]
        real_score = local_result["real_score"]
        combined_fake_score = max(fake_score, filename_score)

        if combined_fake_score >= FAKE_HIGH_THRESHOLD:
            level = "High Risk / Likely AI-Generated"
            risk_score = max(75, combined_fake_score)
        elif combined_fake_score >= FAKE_RECALL_THRESHOLD:
            level = "Suspicious"
            risk_score = max(52 if filename_hits else 45, combined_fake_score)
        else:
            level = "Likely Genuine"
            risk_score = min(30, combined_fake_score)

        cap.release()
        _cleanup(path)

        return {
            "risk_score": risk_score,
            "risk_level": level,
            "frames_analyzed": "local-model",
            "file_size_mb": round(file_size_mb, 2),
            "average_ai_fake_score": combined_fake_score,
            "average_ai_real_score": real_score,
            "maximum_ai_fake_score": combined_fake_score,
            "maximum_ai_real_score": real_score,
            "suspicious_frames": 1 if combined_fake_score >= FAKE_RECALL_THRESHOLD else 0,
            "reasons": reasons + local_result["labels"],
            "advice": "This result uses your locally trained video detector.",
        }

    max_ai_frames = FAST_VIDEO_AI_FRAMES if file_size_mb <= FAST_VIDEO_MB else MAX_AI_FRAMES
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    sample_indexes = _sample_frame_indexes(total_frames, fps, max_ai_frames)

    try:
        for frame_index in sample_indexes:
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
            ret, frame = cap.read()

            if not ret:
                continue

            analyzed_frames += 1

            small = cv2.resize(frame, (320, 180))
            gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)

            blur_score = cv2.Laplacian(gray, cv2.CV_64F).var()

            if blur_score < 45:
                suspicious_points += 12
                reasons.append(f"Frame {analyzed_frames}: possible blur/artifact inconsistency")

            brightness = gray.mean()

            if brightness < 35 or brightness > 220:
                suspicious_points += 10
                reasons.append(f"Frame {analyzed_frames}: abnormal lighting pattern")

            ai_frame = cv2.resize(frame, (320, 320), interpolation=cv2.INTER_AREA)
            frame_path = os.path.join("sampled_frames", f"frame_{analyzed_frames}.jpg")
            cv2.imwrite(frame_path, ai_frame, [cv2.IMWRITE_JPEG_QUALITY, FRAME_JPEG_QUALITY])

            ai_result = check_frame_with_ai(frame_path)
            _cleanup_frame(frame_path)

            fake_score = ai_result["fake_score"]
            real_score = ai_result["real_score"]
            fake_scores.append(fake_score)
            real_scores.append(real_score)
            ai_statuses.append(ai_result["status"])

            reasons.append(
                f"Frame {analyzed_frames}: AI model fake {fake_score}% / real {real_score}% | "
                + ", ".join(ai_result["labels"][:2])
            )

            if fake_score >= FAKE_RECALL_THRESHOLD:
                reasons.append(
                    f"Frame {analyzed_frames}: fake signal crossed recall threshold ({FAKE_RECALL_THRESHOLD}%)"
                )

            if fake_score >= FAKE_HIGH_THRESHOLD:
                suspicious_points += 25
            elif fake_score >= FAKE_SUSPICIOUS_THRESHOLD:
                suspicious_points += 15
            elif fake_score >= FAKE_RECALL_THRESHOLD:
                suspicious_points += 8
            elif real_score and fake_score > real_score:
                suspicious_points += 10

            if fake_score >= 75:
                reasons.append("Stopped early after strong AI-generated signal")
                break
    finally:
        cap.release()
        _cleanup(path)

    if analyzed_frames == 0:
        return {
            "risk_score": 0,
            "risk_level": "Unable to Analyze",
            "reasons": ["Video too short or unreadable"],
            "advice": "Upload a clearer or longer video.",
        }

    working_ai_frames = sum(1 for status in ai_statuses if status == "ok")

    if working_ai_frames == 0:
        level = "AI Model Not Configured"
        score = 0

        if filename_hits:
            level = "Suspicious"
            score = max(52, filename_score)

        return {
            "risk_score": score,
            "risk_level": level,
            "frames_analyzed": analyzed_frames,
            "reasons": reasons[:12],
            "advice": (
                "The AI video model could not run because HF_TOKEN is missing or invalid. "
                "Add HF_TOKEN in Streamlit Secrets and reboot the app."
            ),
        }

    avg_fake_score = int(sum(fake_scores) / len(fake_scores)) if fake_scores else 0
    avg_real_score = int(sum(real_scores) / len(real_scores)) if real_scores else 0
    max_fake_score = max(fake_scores) if fake_scores else 0
    max_real_score = max(real_scores) if real_scores else 0
    suspicious_frame_count = sum(1 for score in fake_scores if score >= FAKE_RECALL_THRESHOLD)
    high_fake_frame_count = sum(1 for score in fake_scores if score >= FAKE_HIGH_THRESHOLD)

    final_score = min(
        100,
        int(
            (avg_fake_score * 0.35)
            + (max_fake_score * 0.45)
            + (suspicious_points * 0.20)
        ),
    )
    final_score = max(final_score, filename_score)

    if high_fake_frame_count >= 1 or max_fake_score >= FAKE_HIGH_THRESHOLD or avg_fake_score >= 35 or final_score >= 60:
        level = "High Risk / Likely AI-Generated"
        final_score = max(final_score, 75 if max_fake_score >= FAKE_HIGH_THRESHOLD else 65)
    elif suspicious_frame_count >= 1 or max_fake_score >= FAKE_RECALL_THRESHOLD or avg_fake_score >= 15 or final_score >= 25:
        level = "Suspicious"
        final_score = max(final_score, 52 if filename_hits else 45)
    elif avg_real_score >= 70 and max_real_score >= 80 and max_fake_score < FAKE_RECALL_THRESHOLD:
        level = "Likely Genuine"
        final_score = min(final_score, 30)
    else:
        level = "Likely Genuine"

    return {
        "risk_score": final_score,
        "risk_level": level,
        "frames_analyzed": analyzed_frames,
        "file_size_mb": round(file_size_mb, 2),
        "average_ai_fake_score": avg_fake_score,
        "average_ai_real_score": avg_real_score,
        "maximum_ai_fake_score": max_fake_score,
        "maximum_ai_real_score": max_real_score,
        "suspicious_frames": suspicious_frame_count,
        "reasons": reasons[:12],
        "advice": (
            "This uses a trained AI frame classifier plus visual artifact checks. "
            "Treat AI-generated or suspicious results carefully."
        ),
    }
