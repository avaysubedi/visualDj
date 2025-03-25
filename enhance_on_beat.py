import cv2
import librosa
import os
import random
from effects import apply_effect

def enhance_video_with_beats(video_path, audio_path, output_path):
    print(f"🎬 Enhancing {video_path} based on {audio_path}")
    y, sr = librosa.load(audio_path)
    beat_frames = librosa.beat.beat_track(y=y, sr=sr)[1]
    beat_times = librosa.frames_to_time(beat_frames, sr=sr)

    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) or 640
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) or 480

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    beat_frame_indexes = set([int(bt * fps) for bt in beat_times])
    current_frame = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.resize(frame, (width, height))

        if current_frame in beat_frame_indexes:
            fx = random.choice(['glitch', 'edgeglow', 'kaleido', 'colorpulse'])
            print(f"💥 Beat at frame {current_frame} → {fx}")
            frame = apply_effect(frame, fx)

        out.write(frame)
        current_frame += 1

    cap.release()
    out.release()
    print(f"✅ Enhanced video saved: {output_path}")
