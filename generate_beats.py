# generate_beats.py
from audio_analysis import extract_beat_times

extract_beat_times("static/music/song.mp3", "static/music/beat_times.json")