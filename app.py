# app.py (Visual DJ Prototype - Complete with MediaPipe Pose Detection)

from flask import Flask, request, render_template, jsonify, send_file, abort
import os
import cv2
import random
import numpy as np
import mimetypes
from urllib.parse import unquote
import mediapipe as mp
import subprocess
import time
from effects import apply_effect, get_random_effect


app = Flask(__name__)
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
PROCESSED_FOLDER = os.path.join(os.getcwd(), 'processed')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

# --- MediaPipe Setup ---
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_drawing = mp.solutions.drawing_utils

# --- Route: Home Upload Page ---
@app.route('/')
def index():
    return render_template('upload.html')

# --- Route: Handle Upload ---
@app.route('/upload', methods=['POST'])
def upload_file():
   try:
        video = request.files['video']
        filename = video.filename.replace(' ', '_')
        timestamp = str(int(time.time()))
        unique_name = f"{timestamp}_{filename}"
        upload_path = os.path.join(UPLOAD_FOLDER, unique_name)
        video.save(upload_path)

        name, _ = os.path.splitext(unique_name)
        processed_filename = f"processed_{name}.mp4"
        processed_path = os.path.join(PROCESSED_FOLDER, processed_filename)

        process_video(upload_path, processed_path)

        return f"✅ Uploaded and processed! <br><a href='/play/{processed_filename}'>Watch Video</a>"
   except Exception as e:
        print(f"❌ Upload error: {e}")
        return "Internal Server Error", 500
# --- Route: Play Single Video ---


@app.route('/play/<filename>')
def play_video(filename):
    return f"<video width='640' height='480' controls autoplay><source src='/processed/{filename}' type='video/mp4'></video>"

# --- Route: Live Visual Wall ---
@app.route('/live')
def live_wall():
    videos = sorted(os.listdir(PROCESSED_FOLDER))
    return render_template('live.html', videos=videos)

# --- API Route: Get Processed Video List ---
@app.route('/api/videos')
def list_processed_videos():
    files = sorted(os.listdir(PROCESSED_FOLDER))
    return jsonify(files)

@app.route('/live-sync')
def live_sync():
    videos = sorted(os.listdir(PROCESSED_FOLDER))
    return render_template('live-sync.html', videos=videos)

# --- Route: Serve Processed Video File ---
@app.route('/processed/<path:filename>')
def serve_processed(filename):
    try:
        safe_filename = unquote(filename)
        full_path = os.path.join(PROCESSED_FOLDER, safe_filename)
        if not os.path.isfile(full_path):
            return abort(404)

        mime_type, _ = mimetypes.guess_type(full_path)
        return send_file(full_path, mimetype=mime_type or 'application/octet-stream')
    except Exception as e:
        print(f"Error: {e}")
        return abort(500)

def reencode_video(input_path):
    temp_path = input_path.replace(".mp4", "_clean.mp4")

    # 🔧 Full path to ffmpeg (adjust this to YOUR exact location)
    FFMPEG_PATH = r"C:\ffmpeg\ffmpeg-7.1.1\bin\ffmpeg.exe"

    command = [
        FFMPEG_PATH, "-y", "-i", input_path,
        "-c:v", "libx264", "-preset", "fast",
        "-crf", "23",
        "-c:a", "aac", "-b:a", "128k",
        "-movflags", "+faststart",
        temp_path
    ]

    try:
        print("🔁 Running ffmpeg reencode...")
        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode != 0:
            print("❌ FFmpeg failed:")
            print(result.stderr)
            raise RuntimeError("FFmpeg returned non-zero exit code.")

        # Replace original file
        os.replace(temp_path, input_path)
        print("✅ FFmpeg re-encoding successful.")

    except FileNotFoundError:
        print("⚠️ FFmpeg not found. Skipping re-encode.")
    except Exception as e:
        print(f"⚠️ Re-encode failed: {e}")


# --- Core Processing Function (MediaPipe Pose Overlay + FX) ---
def process_video(input_path, output_path):
    cap = cv2.VideoCapture(input_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 20.0
    frame_size = (640, 480)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, frame_size)

    # Pick a random effect
    chosen_effect = get_random_effect()
    print(f"🎨 Chosen effect: {chosen_effect}")

   
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.resize(frame, frame_size)
        processed = apply_effect(frame, chosen_effect)
        out.write(processed)

    cap.release()
    out.release()

    try:
        reencode_video(output_path)
    except Exception as e:
        print("⚠️ Re-encode skipped:", e)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)