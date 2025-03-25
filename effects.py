import cv2
import numpy as np
import random

def effect_cartoon(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.medianBlur(gray, 5)
    edges = cv2.adaptiveThreshold(blur, 255,
                cv2.ADAPTIVE_THRESH_MEAN_C,
                cv2.THRESH_BINARY, 9, 9)
    color = cv2.bilateralFilter(frame, 9, 250, 250)
    return cv2.bitwise_and(color, color, mask=edges)

def effect_glitch(frame):
    b, g, r = cv2.split(frame)
    height, width = b.shape
    r = cv2.copyMakeBorder(r, 0, 0, 5, 0, cv2.BORDER_CONSTANT, value=0)
    g = cv2.copyMakeBorder(g, 0, 0, 0, 5, cv2.BORDER_CONSTANT, value=0)
    b = cv2.copyMakeBorder(b, 0, 0, 2, 2, cv2.BORDER_CONSTANT, value=0)
    return cv2.merge((b[:height, :width], g[:height, :width], r[:height, :width]))

def effect_trippy(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    hsv[...,0] = (hsv[...,0] + 50) % 180
    hsv[...,1] = cv2.add(hsv[...,1], 50)
    return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

def effect_edgeglow(frame):
    blur = cv2.GaussianBlur(frame, (5, 5), 0)
    edges = cv2.Canny(blur, 50, 150)
    edges_colored = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
    return cv2.addWeighted(frame, 0.8, edges_colored, 0.4, 0)

def effect_posterize(frame):
    div = 64
    frame = frame // div * div + div // 2
    return frame

# New AI-style FX coming in hot 🔥

def effect_kaleido(frame):
    h, w = frame.shape[:2]
    half = frame[:, :w//2]
    mirror = cv2.flip(half, 1)
    return np.hstack((half, mirror))

def effect_noise_trail(frame):
    noise = np.random.normal(0, 25, frame.shape).astype(np.uint8)
    return cv2.add(frame, noise)

def effect_color_pulse(frame, pulse_amount=30):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    hsv[..., 2] = cv2.add(hsv[..., 2], pulse_amount)
    return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

def effect_hue_cyclone(frame):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    hue_shift = random.randint(30, 120)
    hsv[:, :, 0] = (hsv[:, :, 0] + hue_shift) % 180
    return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

def effect_blur_dream(frame):
    return cv2.GaussianBlur(frame, (15, 15), 0)

def effect_zoom_punch(frame):
    h, w = frame.shape[:2]
    zoomed = cv2.resize(frame, None, fx=1.2, fy=1.2)
    x_start = (zoomed.shape[1] - w) // 2
    y_start = (zoomed.shape[0] - h) // 2
    return zoomed[y_start:y_start+h, x_start:x_start+w]

def effect_rgb_glitch_burst(frame):
    b, g, r = cv2.split(frame)
    height, width = frame.shape[:2]
    shift = 5 + random.randint(0, 10)
    r = np.roll(r, shift, axis=1)
    g = np.roll(g, -shift, axis=0)
    merged = cv2.merge((b, g, r))

    dx = random.randint(-5, 5)
    dy = random.randint(-5, 5)
    M = np.float32([[1, 0, dx], [0, 1, dy]])
    return cv2.warpAffine(merged, M, (width, height))

def effect_flash_burn(frame):
    white_overlay = np.full(frame.shape, 255, dtype=np.uint8)
    return cv2.addWeighted(frame, 0.7, white_overlay, 0.8, 0)

# 🎯 Apply effect
def apply_effect(frame, name):
    func = EFFECTS.get(name, lambda f: f)
    return func(frame)

# 🎲 Get random effect name
def get_random_effect():
    return random.choice(list(EFFECTS.keys()))
# Effect registry
EFFECTS = {
    'cartoon': effect_cartoon,
    'glitch': effect_glitch,
    'trippy': effect_trippy,
    'edgeglow': effect_edgeglow,
    'posterize': effect_posterize,
    'kaleido': effect_kaleido,
    'noisetrail': effect_noise_trail,
    'colorpulse': effect_color_pulse,
    'rgb_glitch_burst': effect_rgb_glitch_burst,
    'flash_burn': effect_flash_burn,
    'hue_cyclone': effect_hue_cyclone,
    'zoom_punch': effect_zoom_punch,
    'blur_dream': effect_blur_dream
}
