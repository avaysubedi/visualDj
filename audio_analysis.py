import librosa
import json

def extract_beat_times(audio_path, output_json):
    y, sr = librosa.load(audio_path)
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
    beat_times = librosa.frames_to_time(beats, sr=sr)

    with open(output_json, 'w') as f:
        json.dump(beat_times.tolist(), f)

    print(f"✅ Beat times saved to {output_json}")
