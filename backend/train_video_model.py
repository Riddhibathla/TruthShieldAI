import argparse
import os

import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split

from local_video_model import FEATURE_VERSION, extract_video_features


VIDEO_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv", ".webm"}


def _iter_videos(folder):
    for root, _, files in os.walk(folder):
        for filename in files:
            if os.path.splitext(filename)[1].lower() in VIDEO_EXTENSIONS:
                yield os.path.join(root, filename)


def _load_dataset(dataset_dir, max_frames):
    samples = []
    labels = []

    for label_name, label_value in [("real", 0), ("fake", 1)]:
        folder = os.path.join(dataset_dir, label_name)

        if not os.path.isdir(folder):
            raise FileNotFoundError(f"Missing folder: {folder}")

        for video_path in _iter_videos(folder):
            print(f"Extracting {label_name}: {video_path}")
            try:
                samples.append(extract_video_features(video_path, max_frames=max_frames))
                labels.append(label_value)
            except Exception as exc:
                print(f"Skipping {video_path}: {exc}")

    if len(samples) < 6:
        raise ValueError("Add at least 3 real and 3 fake videos before training.")

    if len(set(labels)) != 2:
        raise ValueError("Training needs both real and fake videos.")

    return np.vstack(samples), np.array(labels)


def train(dataset_dir, output_path, max_frames):
    features, labels = _load_dataset(dataset_dir, max_frames)

    stratify = labels if min(np.bincount(labels)) >= 2 else None
    x_train, x_test, y_train, y_test = train_test_split(
        features,
        labels,
        test_size=0.25,
        random_state=42,
        stratify=stratify,
    )

    model = RandomForestClassifier(
        n_estimators=350,
        min_samples_leaf=2,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
    )
    model.fit(x_train, y_train)

    predictions = model.predict(x_test)
    report = classification_report(
        y_test,
        predictions,
        target_names=["real", "fake"],
        zero_division=0,
    )

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    joblib.dump(
        {
            "model": model,
            "feature_version": FEATURE_VERSION,
            "max_frames": max_frames,
            "classification_report": report,
        },
        output_path,
    )

    print("\nValidation report")
    print(report)
    print(f"Saved model to {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Train a local AI-vs-real video detector.")
    parser.add_argument("--dataset", default="training_videos")
    parser.add_argument("--output", default=os.path.join("models", "video_ai_detector.joblib"))
    parser.add_argument("--max-frames", type=int, default=12)
    args = parser.parse_args()

    train(args.dataset, args.output, args.max_frames)


if __name__ == "__main__":
    main()
