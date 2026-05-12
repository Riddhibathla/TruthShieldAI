import os

import cv2

from ai_frame_detector import check_frame_with_ai

MAX_AI_FRAMES = int(os.getenv("VIDEO_MAX_AI_FRAMES", "4"))
FRAME_JPEG_QUALITY = int(os.getenv("VIDEO_FRAME_JPEG_QUALITY", "70"))


def _cleanup(path):
    if path and os.path.exists(path):
        os.remove(path)


def _cleanup_frame(path):
    if path and os.path.exists(path):
        os.remove(path)


def _sample_frame_indexes(total_frames, fps):
    if total_frames and total_frames > 0:
        start = max(1, int(fps) if fps and fps > 0 else 1)
        end = max(start + 1, total_frames - 1)
        if MAX_AI_FRAMES == 1:
            return [min(start, end)]

        step = max(1, (end - start) // MAX_AI_FRAMES)
        return [min(end, start + (i * step)) for i in range(MAX_AI_FRAMES)]

    interval = max(30, int((fps or 30) * 1.5))
    return [interval * (i + 1) for i in range(MAX_AI_FRAMES)]


def analyze_video(path):
    cap = cv2.VideoCapture(path)

    analyzed_frames = 0
    fake_scores = []
    real_scores = []
    suspicious_points = 0
    ai_statuses = []
    reasons = []

    os.makedirs("sampled_frames", exist_ok=True)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    sample_indexes = _sample_frame_indexes(total_frames, fps)

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

            ai_frame = cv2.resize(frame, (384, 216), interpolation=cv2.INTER_AREA)
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

            if fake_score >= 55:
                suspicious_points += 25
            elif fake_score >= 35:
                suspicious_points += 15

            if fake_score >= 80 and analyzed_frames >= 2:
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
        return {
            "risk_score": min(100, suspicious_points),
            "risk_level": "Unable to Run AI Model",
            "frames_analyzed": analyzed_frames,
            "reasons": reasons[:12],
            "advice": "The AI video model could not run. Check HF_TOKEN and backend network access, then retry.",
        }

    avg_fake_score = int(sum(fake_scores) / len(fake_scores)) if fake_scores else 0
    avg_real_score = int(sum(real_scores) / len(real_scores)) if real_scores else 0

    final_score = min(
        100,
        int((avg_fake_score * 0.75) + (suspicious_points * 0.25)),
    )

    if avg_fake_score >= 60 or final_score >= 70:
        level = "High Risk / Likely AI-Generated"
        final_score = max(final_score, 75)
    elif avg_fake_score >= 35 or final_score >= 35:
        level = "Suspicious"
        final_score = max(final_score, 45)
    elif avg_real_score >= 60 and avg_fake_score < 35:
        level = "Likely Genuine"
        final_score = min(final_score, 30)
    else:
        level = "Likely Genuine"

    return {
        "risk_score": final_score,
        "risk_level": level,
        "frames_analyzed": analyzed_frames,
        "average_ai_fake_score": avg_fake_score,
        "average_ai_real_score": avg_real_score,
        "reasons": reasons[:12],
        "advice": (
            "This uses a trained AI frame classifier plus visual artifact checks. "
            "Treat AI-generated or suspicious results carefully."
        ),
    }
