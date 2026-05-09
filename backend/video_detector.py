import cv2
import os
from ai_frame_detector import check_frame_with_ai

def analyze_video(path):
    cap = cv2.VideoCapture(path)

    frame_count = 0
    analyzed_frames = 0
    ai_scores = []
    suspicious_points = 0
    reasons = []

    os.makedirs("sampled_frames", exist_ok=True)

    while True:
        ret, frame = cap.read()

        if not ret:
            break

        frame_count += 1

        # Analyze every 30th frame
        if frame_count % 30 == 0:

            analyzed_frames += 1

            # Resize for faster processing
            small = cv2.resize(frame, (320, 180))

            gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)

            # -------------------------------
            # Blur / artifact detection
            # -------------------------------
            blur_score = cv2.Laplacian(
                gray,
                cv2.CV_64F
            ).var()

            if blur_score < 45:
                suspicious_points += 12

                reasons.append(
                    f"Frame {analyzed_frames}: possible blur/artifact inconsistency"
                )

            # -------------------------------
            # Lighting inconsistency
            # -------------------------------
            brightness = gray.mean()

            if brightness < 35 or brightness > 220:
                suspicious_points += 10

                reasons.append(
                    f"Frame {analyzed_frames}: abnormal lighting pattern"
                )

            # -------------------------------
            # Save frame temporarily
            # -------------------------------
            frame_path = f"sampled_frames/frame_{analyzed_frames}.jpg"

            cv2.imwrite(frame_path, frame)

            # -------------------------------
            # AI model analysis
            # -------------------------------
            ai_score, labels = check_frame_with_ai(frame_path)

            ai_scores.append(ai_score)

            reasons.append(
                f"Frame {analyzed_frames}: AI model score {ai_score}% | {', '.join(labels[:2])}"
            )

            # Extra suspicion for higher AI score
            if ai_score >= 40:
                suspicious_points += 15

            os.remove(frame_path)

        # Analyze max 10 frames
        if analyzed_frames >= 10:
            break

    cap.release()

    # Cleanup uploaded video
    if os.path.exists(path):
        os.remove(path)

    # ---------------------------------------
    # Safety check
    # ---------------------------------------
    if analyzed_frames == 0:

        return {
            "risk_score": 0,
            "risk_level": "Unable to Analyze",
            "reasons": [
                "Video too short or unreadable"
            ],
            "advice": "Upload a clearer or longer video."
        }

    # ---------------------------------------
    # Average AI score
    # ---------------------------------------
    avg_ai_score = int(
        sum(ai_scores) / len(ai_scores)
    ) if ai_scores else 0

    # ---------------------------------------
    # Modern AI video heuristic
    # ---------------------------------------
    if avg_ai_score <= 5:
        suspicious_points += 20

    # ---------------------------------------
    # Final hybrid score
    # ---------------------------------------
    final_score = min(
        100,
        int(
            (avg_ai_score * 0.6)
            +
            (suspicious_points * 0.4)
        )
    )

    # ---------------------------------------
    # Risk levels
    # ---------------------------------------
    if final_score >= 70:

        level = "High Risk / Likely AI-Generated"

    elif final_score >= 35:

        level = "Suspicious"
        final_score = max(final_score, 95)

    elif avg_ai_score <= 5 and analyzed_frames >= 3:

        level = "Potentially AI-Enhanced"
        final_score = max(final_score, 67)

    else:

        level = "Likely Genuine"

    # ---------------------------------------
    # Return analysis
    # ---------------------------------------
    return {

        "risk_score": final_score,

        "risk_level": level,

        "frames_analyzed": analyzed_frames,

        "reasons": reasons[:12],

        "advice":
        "This is a hybrid frame-level analysis using AI model scoring plus visual inconsistency checks. Highly realistic AI videos may still require advanced forensic analysis."
    }