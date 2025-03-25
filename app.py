from flask import Flask, Response, render_template, request
import cv2
import os
import time
import json
import random
from effects import apply_effect

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Load beat times once
with open('static/music/beat_times.json') as f:
    beat_times = json.load(f)

def get_video_paths():
    files = sorted(os.listdir(UPLOAD_FOLDER))
    return [os.path.join(UPLOAD_FOLDER, f) for f in files if f.endswith('.mp4') or f.endswith('.mov')]

def generate_frames():
    video_paths = get_video_paths()
    if not video_paths:
        return

    video_index = 0
    cap = cv2.VideoCapture(video_paths[video_index])
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    beat_frames = [int(bt * fps) for bt in beat_times]
    frame_index = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            video_index = (video_index + 1) % len(video_paths)
            cap.release()
            cap = cv2.VideoCapture(video_paths[video_index])
            fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
            beat_frames = [int(bt * fps) for bt in beat_times]
            frame_index = 0
            continue

        frame = cv2.resize(frame, (640, 480))

        if frame_index in beat_frames:
            fx = random.choice(['cartoon', 'glitch', 'hue_cyclone', 'rgb_glitch_burst'])
            frame = apply_effect(frame, fx)

        _, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

        frame_index += 1
        time.sleep(1 / fps)

@app.route('/')
def upload_page():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['video']
    file.save(os.path.join(UPLOAD_FOLDER, file.filename))
    return "Uploaded successfully! <br><a href='/live-view'>Go to Live FX</a>"

@app.route('/live-view')
def live_view():
    return render_template('live.html')

@app.route('/live-fx-stream')
def live_fx_stream():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(debug=True)
