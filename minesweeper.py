import ctypes
try:
    ctypes.windll.user32.SetProcessDPIAware()
except Exception:
    pass

import os
os.environ['SDL_VIDEO_CENTERED'] = '1'

import pygame
import random
import math
import struct
import io
import json
import time
from collections import deque

# --- Constants ---
CELL_SIZE = 48
BORDER_W = 2
TOP_BAR_H = 56
BOTTOM_BAR_H = 30
FPS = 60

DIFFICULTIES = {
    "easy": (9, 9, 10),
    "medium": (16, 16, 40),
    "expert": (30, 16, 99),
}

COL_WHITE = (255, 255, 255)
COL_BLACK = (0, 0, 0)
COL_OVERLAY = (0, 0, 0, 140)

SCORES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "minesweeper_scores.json")

# --- Themes ---
THEMES = [
    {
        "id": "classic",
        "name": "CLASSIC",
        "bg": (0x6B, 0x3A, 0x2A),
        "unrevealed": (0xD4, 0xA5, 0x74),
        "revealed": (0xF0, 0xD5, 0xB0),
        "border_light": (0xE8, 0xC9, 0xA0),
        "border_dark": (0xA0, 0x78, 0x50),
        "grid_line": (0x8B, 0x5E, 0x3C),
        "top_bar": (0x8B, 0x5E, 0x3C),
        "hover": (0xDE, 0xB3, 0x84),
        "pressed": (0xC0, 0x95, 0x64),
        "exploded": (0xE0, 0x40, 0x40),
        "win_flash": (0x80, 0xE0, 0x80),
        "button_bg": (0x6B, 0x3A, 0x2A),
        "button_active": (0xD4, 0xA5, 0x74),
        "button_text": (0xF0, 0xD5, 0xB0),
        "num_colors": {
            1: (0x00, 0x00, 0xFF), 2: (0x00, 0x80, 0x00),
            3: (0xFF, 0x00, 0x00), 4: (0x00, 0x00, 0x80),
            5: (0x80, 0x00, 0x00), 6: (0x00, 0x80, 0x80),
            7: (0x00, 0x00, 0x00), 8: (0x80, 0x80, 0x80),
        },
        "flag_sprite": [
            '0011000',
            '0111000',
            '1111000',
            '0011000',
            '0011000',
            '0011000',
            '0011000',
            '0011000',
            '1111111',
        ],
        "flag_colors": {'1': (0xDC, 0x14, 0x3C)},
        "flag_x_color": (0xDC, 0x14, 0x3C),
    },
    {
        "id": "autumn",
        "name": "AUTUMN",
        "bg": (0x5A, 0x2E, 0x0E),
        "unrevealed": (0xE8, 0x7A, 0x20),
        "revealed": (0xF5, 0xE6, 0xCA),
        "border_light": (0xF0, 0x9E, 0x50),
        "border_dark": (0xB0, 0x5A, 0x15),
        "grid_line": (0x6B, 0x3A, 0x15),
        "top_bar": (0x6B, 0x3A, 0x15),
        "hover": (0xF0, 0x90, 0x40),
        "pressed": (0xC8, 0x68, 0x18),
        "exploded": (0xCC, 0x33, 0x00),
        "win_flash": (0xFF, 0xD7, 0x00),
        "button_bg": (0x5A, 0x2E, 0x0E),
        "button_active": (0xE8, 0x7A, 0x20),
        "button_text": (0xF5, 0xE6, 0xCA),
        "num_colors": {
            1: (0x22, 0x66, 0xAA), 2: (0x44, 0x88, 0x22),
            3: (0xCC, 0x33, 0x00), 4: (0x66, 0x33, 0x00),
            5: (0x88, 0x22, 0x00), 6: (0x00, 0x77, 0x66),
            7: (0x33, 0x22, 0x00), 8: (0x88, 0x77, 0x55),
        },
        "flag_sprite": [
            '0002000',
            '0122210',
            '0222220',
            '0111110',
            '0111110',
            '0111110',
            '0111110',
            '0011100',
            '0001000',
        ],
        "flag_colors": {'1': (0xD4, 0xA0, 0x50), '2': (0x6B, 0x3A, 0x15)},
        "flag_x_color": (0xCC, 0x33, 0x00),
    },
    {
        "id": "midnight",
        "name": "MIDNIGHT",
        "bg": (0x1E, 0x22, 0x38),
        "unrevealed": (0x44, 0x4C, 0x6A),
        "revealed": (0xC0, 0xC8, 0xDC),
        "border_light": (0x60, 0x68, 0x88),
        "border_dark": (0x2A, 0x30, 0x4A),
        "grid_line": (0x35, 0x3B, 0x55),
        "top_bar": (0x28, 0x2E, 0x48),
        "hover": (0x5A, 0x64, 0x84),
        "pressed": (0x38, 0x40, 0x5C),
        "exploded": (0xFF, 0x44, 0x55),
        "win_flash": (0x88, 0xFF, 0xCC),
        "button_bg": (0x1E, 0x22, 0x38),
        "button_active": (0x44, 0x4C, 0x6A),
        "button_text": (0xC0, 0xC8, 0xDC),
        "num_colors": {
            1: (0x44, 0x88, 0xCC), 2: (0x22, 0x88, 0x44),
            3: (0xCC, 0x33, 0x55), 4: (0x55, 0x33, 0xAA),
            5: (0x88, 0x22, 0x44), 6: (0x00, 0x88, 0x88),
            7: (0x22, 0x22, 0x44), 8: (0x66, 0x66, 0x88),
        },
        "flag_sprite": [
            '0022200',
            '0222210',
            '2222110',
            '2222110',
            '2222110',
            '2222110',
            '0222210',
            '0022200',
            '0000000',
        ],
        "flag_colors": {'1': (0xFF, 0xD7, 0x00), '2': (0x18, 0x1C, 0x28)},
        "flag_x_color": (0xFF, 0x44, 0x55),
    },
    {
        "id": "lavender",
        "name": "LAVENDER",
        "bg": (0x4A, 0x30, 0x60),
        "unrevealed": (0x9B, 0x6B, 0xBB),
        "revealed": (0xE8, 0xDD, 0xF0),
        "border_light": (0xBB, 0x88, 0xDD),
        "border_dark": (0x6A, 0x44, 0x88),
        "grid_line": (0x5A, 0x3A, 0x70),
        "top_bar": (0x5A, 0x3A, 0x70),
        "hover": (0xAA, 0x7B, 0xCC),
        "pressed": (0x7A, 0x55, 0x99),
        "exploded": (0xDD, 0x44, 0x66),
        "win_flash": (0xCC, 0xEE, 0xFF),
        "button_bg": (0x4A, 0x30, 0x60),
        "button_active": (0x9B, 0x6B, 0xBB),
        "button_text": (0xE8, 0xDD, 0xF0),
        "num_colors": {
            1: (0x33, 0x66, 0xCC), 2: (0x33, 0x99, 0x44),
            3: (0xCC, 0x22, 0x44), 4: (0x55, 0x22, 0x88),
            5: (0x88, 0x11, 0x33), 6: (0x00, 0x77, 0x77),
            7: (0x22, 0x11, 0x33), 8: (0x77, 0x66, 0x88),
        },
        "flag_sprite": [
            '2000020',
            '0200200',
            '1110111',
            '1111111',
            '0022200',
            '1111111',
            '1110111',
            '0100010',
            '0000000',
        ],
        "flag_colors": {'1': (0xEE, 0xBB, 0xFF), '2': (0x55, 0x22, 0x77)},
        "flag_x_color": (0xDD, 0x44, 0x66),
    },
]

# --- Pixel Font (5x7) ---
PIXEL_FONT = {
    '0': ['01110', '10001', '10011', '10101', '11001', '10001', '01110'],
    '1': ['00100', '01100', '00100', '00100', '00100', '00100', '01110'],
    '2': ['01110', '10001', '00001', '00110', '01000', '10000', '11111'],
    '3': ['01110', '10001', '00001', '00110', '00001', '10001', '01110'],
    '4': ['00010', '00110', '01010', '10010', '11111', '00010', '00010'],
    '5': ['11111', '10000', '11110', '00001', '00001', '10001', '01110'],
    '6': ['00110', '01000', '10000', '11110', '10001', '10001', '01110'],
    '7': ['11111', '00001', '00010', '00100', '01000', '01000', '01000'],
    '8': ['01110', '10001', '10001', '01110', '10001', '10001', '01110'],
    '9': ['01110', '10001', '10001', '01111', '00001', '00010', '01100'],
    'A': ['01110', '10001', '10001', '11111', '10001', '10001', '10001'],
    'B': ['11110', '10001', '10001', '11110', '10001', '10001', '11110'],
    'C': ['01110', '10001', '10000', '10000', '10000', '10001', '01110'],
    'D': ['11110', '10001', '10001', '10001', '10001', '10001', '11110'],
    'E': ['11111', '10000', '10000', '11110', '10000', '10000', '11111'],
    'F': ['11111', '10000', '10000', '11110', '10000', '10000', '10000'],
    'G': ['01110', '10001', '10000', '10111', '10001', '10001', '01110'],
    'H': ['10001', '10001', '10001', '11111', '10001', '10001', '10001'],
    'I': ['01110', '00100', '00100', '00100', '00100', '00100', '01110'],
    'J': ['00111', '00010', '00010', '00010', '00010', '10010', '01100'],
    'K': ['10001', '10010', '10100', '11000', '10100', '10010', '10001'],
    'L': ['10000', '10000', '10000', '10000', '10000', '10000', '11111'],
    'M': ['10001', '11011', '10101', '10101', '10001', '10001', '10001'],
    'N': ['10001', '11001', '10101', '10011', '10001', '10001', '10001'],
    'O': ['01110', '10001', '10001', '10001', '10001', '10001', '01110'],
    'P': ['11110', '10001', '10001', '11110', '10000', '10000', '10000'],
    'Q': ['01110', '10001', '10001', '10001', '10101', '10010', '01101'],
    'R': ['11110', '10001', '10001', '11110', '10100', '10010', '10001'],
    'S': ['01110', '10001', '10000', '01110', '00001', '10001', '01110'],
    'T': ['11111', '00100', '00100', '00100', '00100', '00100', '00100'],
    'U': ['10001', '10001', '10001', '10001', '10001', '10001', '01110'],
    'V': ['10001', '10001', '10001', '10001', '01010', '01010', '00100'],
    'W': ['10001', '10001', '10001', '10101', '10101', '11011', '10001'],
    'X': ['10001', '10001', '01010', '00100', '01010', '10001', '10001'],
    'Y': ['10001', '10001', '01010', '00100', '00100', '00100', '00100'],
    'Z': ['11111', '00001', '00010', '00100', '01000', '10000', '11111'],
    ':': ['00000', '00100', '00100', '00000', '00100', '00100', '00000'],
    '-': ['00000', '00000', '00000', '11111', '00000', '00000', '00000'],
    '!': ['00100', '00100', '00100', '00100', '00100', '00000', '00100'],
    ' ': ['00000', '00000', '00000', '00000', '00000', '00000', '00000'],
    '>': ['00000', '01000', '00100', '00010', '00100', '01000', '00000'],
}


def render_pixel_text(text, color, scale=3):
    text = text.upper()
    char_w = 5 * scale
    char_h = 7 * scale
    spacing = scale
    total_w = len(text) * (char_w + spacing) - spacing if text else 0
    surf = pygame.Surface((max(total_w, 1), char_h), pygame.SRCALPHA)
    x = 0
    for ch in text:
        glyph = PIXEL_FONT.get(ch)
        if glyph is None:
            x += char_w + spacing
            continue
        for row_i, row in enumerate(glyph):
            for col_i, px in enumerate(row):
                if px == '1':
                    pygame.draw.rect(surf, color,
                                     (x + col_i * scale, row_i * scale, scale, scale))
        x += char_w + spacing
    return surf


# --- Sound Generation ---
def _make_wav_bytes(samples, sample_rate=22050):
    raw = struct.pack(f'<{len(samples)}h', *samples)
    buf = io.BytesIO()
    buf.write(b'RIFF')
    data_size = len(raw)
    buf.write(struct.pack('<I', 36 + data_size))
    buf.write(b'WAVE')
    buf.write(b'fmt ')
    buf.write(struct.pack('<IHHIIHH', 16, 1, 1, sample_rate, sample_rate * 2, 2, 16))
    buf.write(b'data')
    buf.write(struct.pack('<I', data_size))
    buf.write(raw)
    buf.seek(0)
    return buf


def _tone(freq, duration, volume=0.3, sr=22050):
    n = int(sr * duration)
    samples = []
    for i in range(n):
        t = i / sr
        env = max(0, 1.0 - i / n)
        val = math.sin(2 * math.pi * freq * t) * volume * env
        samples.append(max(-32767, min(32767, int(val * 32767))))
    return samples


def _noise(duration, volume=0.3, sr=22050):
    n = int(sr * duration)
    return [max(-32767, min(32767, int((random.random() * 2 - 1) * volume * max(0, 1.0 - i / n) * 32767))) for i in range(n)]


def _sweep(f1, f2, duration, volume=0.3, sr=22050):
    n = int(sr * duration)
    samples = []
    for i in range(n):
        t = i / sr
        phase = 2 * math.pi * (f1 * t + (f2 - f1) * t * t / (2 * duration))
        env = max(0, 1.0 - i / n)
        samples.append(max(-32767, min(32767, int(math.sin(phase) * volume * env * 32767))))
    return samples


def _silence(duration, sr=22050):
    return [0] * int(sr * duration)


def _make_sound(samples, sr=22050):
    return pygame.mixer.Sound(buffer=_make_wav_bytes(samples, sr).read())


def generate_sounds(theme_id):
    sounds = {}
    sr = 22050

    if theme_id == "classic":
        sounds['click'] = _make_sound(_tone(800, 0.05, 0.2, sr), sr)
        sounds['flag_place'] = _make_sound(_tone(1200, 0.08, 0.25, sr), sr)
        sounds['flag_remove'] = _make_sound(_tone(600, 0.08, 0.2, sr), sr)

        boom = []
        n = int(sr * 0.4)
        for i in range(n):
            t = i / sr
            env = max(0, 1.0 - i / n) ** 2
            val = (math.sin(2 * math.pi * 80 * t) * 0.5 +
                   math.sin(2 * math.pi * 50 * t) * 0.3 +
                   (random.random() * 2 - 1) * 0.2) * env * 0.4
            boom.append(max(-32767, min(32767, int(val * 32767))))
        sounds['explode'] = _make_sound(boom, sr)

        win = []
        for freq in [523, 659, 784]:
            note_len = int(sr * 0.15)
            for i in range(note_len):
                t = i / sr
                env = max(0, 1.0 - (i / note_len) * 0.5)
                val = math.sin(2 * math.pi * freq * t) * 0.3 * env
                win.append(max(-32767, min(32767, int(val * 32767))))
        sounds['win'] = _make_sound(win, sr)

        sounds['btn_easy'] = _make_sound(_tone(440, 0.06, 0.25, sr) + _tone(550, 0.06, 0.25, sr), sr)
        sounds['btn_medium'] = _make_sound(_tone(550, 0.05, 0.25, sr) + _tone(700, 0.05, 0.25, sr) + _tone(550, 0.05, 0.25, sr), sr)
        sounds['btn_expert'] = _make_sound(_tone(700, 0.04, 0.25, sr) + _tone(880, 0.04, 0.25, sr) + _tone(1100, 0.04, 0.25, sr) + _tone(880, 0.04, 0.25, sr), sr)

    elif theme_id == "autumn":
        sounds['click'] = _make_sound(_tone(200, 0.03, 0.35, sr) + _tone(150, 0.05, 0.25, sr) + _noise(0.02, 0.08, sr), sr)

        rustle = _noise(0.06, 0.12, sr)
        thud = _tone(250, 0.04, 0.1, sr)
        sounds['flag_place'] = _make_sound(rustle + thud, sr)
        sounds['flag_remove'] = _make_sound(thud + _noise(0.05, 0.1, sr), sr)

        crack = []
        for burst in range(4):
            crack += _noise(0.02, 0.25 * (1 - burst * 0.2), sr)
            crack += _silence(0.03, sr)
        crack += _tone(100, 0.15, 0.15, sr)
        sounds['explode'] = _make_sound(crack, sr)

        win = []
        for freq in [262, 330, 392, 523]:
            dur = 0.2 if freq < 500 else 0.3
            note_len = int(sr * dur)
            for i in range(note_len):
                t = i / sr
                env = max(0, 1.0 - (i / note_len) * 0.6)
                val = math.sin(2 * math.pi * freq * t) * 0.25 * env
                win.append(max(-32767, min(32767, int(val * 32767))))
        sounds['win'] = _make_sound(win, sr)

        sounds['btn_easy'] = _make_sound(_tone(180, 0.06, 0.3, sr) + _noise(0.02, 0.05, sr), sr)
        sounds['btn_medium'] = _make_sound(_tone(180, 0.05, 0.25, sr) + _silence(0.04, sr) + _tone(200, 0.05, 0.25, sr) + _noise(0.02, 0.04, sr), sr)
        sounds['btn_expert'] = _make_sound(_tone(180, 0.04, 0.2, sr) + _silence(0.03, sr) + _tone(200, 0.04, 0.2, sr) + _silence(0.03, sr) + _tone(220, 0.04, 0.2, sr) + _noise(0.02, 0.03, sr), sr)

    elif theme_id == "midnight":
        sounds['click'] = _make_sound(_tone(500, 0.03, 0.2, sr) + _tone(500, 0.1, 0.08, sr), sr)
        sounds['flag_place'] = _make_sound(_sweep(2000, 300, 0.12, 0.2, sr) + _noise(0.06, 0.04, sr), sr)
        sounds['flag_remove'] = _make_sound(_sweep(300, 1800, 0.12, 0.18, sr) + _noise(0.05, 0.03, sr), sr)

        rumble = []
        n = int(sr * 0.5)
        for i in range(n):
            t = i / sr
            env = max(0, 1.0 - i / n) ** 1.5
            val = (math.sin(2 * math.pi * 55 * t) * 0.4 +
                   math.sin(2 * math.pi * 40 * t) * 0.3 +
                   (random.random() * 2 - 1) * 0.15) * env * 0.35
            rumble.append(max(-32767, min(32767, int(val * 32767))))
        sounds['explode'] = _make_sound(rumble, sr)

        win = []
        for freq in [1047, 1319, 1568, 2093]:
            note_len = int(sr * 0.18)
            for i in range(note_len):
                t = i / sr
                env = max(0, 1.0 - (i / note_len) * 0.4)
                val = (math.sin(2 * math.pi * freq * t) * 0.15 +
                       math.sin(2 * math.pi * freq * 2 * t) * 0.05) * env
                win.append(max(-32767, min(32767, int(val * 32767))))
        sounds['win'] = _make_sound(win, sr)

        sounds['btn_easy'] = _make_sound(_tone(220, 0.15, 0.15, sr), sr)
        sounds['btn_medium'] = _make_sound(_sweep(220, 440, 0.15, 0.2, sr), sr)
        sounds['btn_expert'] = _make_sound(_sweep(880, 220, 0.2, 0.22, sr), sr)

    elif theme_id == "lavender":
        bell = []
        n = int(sr * 0.08)
        for i in range(n):
            t = i / sr
            env = math.exp(-i / n * 4)
            val = (math.sin(2 * math.pi * 1200 * t) * 0.2 +
                   math.sin(2 * math.pi * 2400 * t) * 0.06) * env
            bell.append(max(-32767, min(32767, int(val * 32767))))
        sounds['click'] = _make_sound(bell, sr)

        flutter = []
        n = int(sr * 0.1)
        for i in range(n):
            t = i / sr
            env = max(0, 1.0 - i / n)
            trem = 0.5 + 0.5 * math.sin(2 * math.pi * 25 * t)
            val = math.sin(2 * math.pi * 800 * t) * 0.2 * env * trem
            flutter.append(max(-32767, min(32767, int(val * 32767))))
        sounds['flag_place'] = _make_sound(flutter, sr)

        unflutter = []
        n = int(sr * 0.08)
        for i in range(n):
            t = i / sr
            env = max(0, 1.0 - i / n)
            trem = 0.5 + 0.5 * math.sin(2 * math.pi * 20 * t)
            val = math.sin(2 * math.pi * 600 * t) * 0.15 * env * trem
            unflutter.append(max(-32767, min(32767, int(val * 32767))))
        sounds['flag_remove'] = _make_sound(unflutter, sr)

        sounds['explode'] = _make_sound(_sweep(1500, 400, 0.2, 0.2, sr) + _noise(0.08, 0.06, sr), sr)

        win = []
        for freq in [784, 988, 1175, 1568]:
            note_len = int(sr * 0.12)
            for i in range(note_len):
                t = i / sr
                env = math.exp(-i / note_len * 3)
                val = (math.sin(2 * math.pi * freq * t) * 0.2 +
                       math.sin(2 * math.pi * freq * 3 * t) * 0.04) * env
                win.append(max(-32767, min(32767, int(val * 32767))))
        sounds['win'] = _make_sound(win, sr)

        chime_base = []
        n = int(sr * 0.1)
        for i in range(n):
            t = i / sr
            env = math.exp(-i / n * 3)
            val = math.sin(2 * math.pi * 880 * t) * 0.2 * env
            chime_base.append(max(-32767, min(32767, int(val * 32767))))
        sounds['btn_easy'] = _make_sound(chime_base, sr)

        chime2 = []
        for freq in [880, 1047]:
            n = int(sr * 0.08)
            for i in range(n):
                t = i / sr
                env = math.exp(-i / n * 3)
                val = math.sin(2 * math.pi * freq * t) * 0.18 * env
                chime2.append(max(-32767, min(32767, int(val * 32767))))
        sounds['btn_medium'] = _make_sound(chime2, sr)

        chime3 = []
        for freq in [880, 1047, 1319]:
            n = int(sr * 0.07)
            for i in range(n):
                t = i / sr
                env = math.exp(-i / n * 3)
                val = math.sin(2 * math.pi * freq * t) * 0.18 * env
                chime3.append(max(-32767, min(32767, int(val * 32767))))
        sounds['btn_expert'] = _make_sound(chime3, sr)

    return sounds


# --- Sprite Drawing ---
def draw_flag(surface, rect, sprite, colors):
    cols = len(sprite[0])
    rows = len(sprite)
    px = min(rect.width // (cols + 2), rect.height // (rows + 2))
    gw = cols * px
    gh = rows * px
    ox = rect.x + (rect.width - gw) // 2
    oy = rect.y + (rect.height - gh) // 2
    for row_i, row in enumerate(sprite):
        for col_i, ch in enumerate(row):
            if ch != '0' and ch in colors:
                pygame.draw.rect(surface, colors[ch],
                                 (ox + col_i * px, oy + row_i * px, px, px))


def draw_flag_wiped(surface, rect, sprite, colors, wipe_progress):
    num_cols = len(sprite[0])
    rows = len(sprite)
    ps = min(rect.width // (num_cols + 2), rect.height // (rows + 2))
    gw = num_cols * ps
    gh = rows * ps
    ox = rect.x + (rect.width - gw) // 2
    oy = rect.y + (rect.height - gh) // 2

    cols_wiped_float = wipe_progress * num_cols
    fully_wiped = int(cols_wiped_float)
    partial_frac = cols_wiped_float - fully_wiped

    for row_i, row in enumerate(sprite):
        for col_i, ch in enumerate(row):
            if ch != '0' and ch in colors:
                col_from_right = num_cols - 1 - col_i
                if col_from_right < fully_wiped:
                    continue
                color = colors[ch]
                if col_from_right == fully_wiped and partial_frac > 0:
                    alpha = int(255 * (1.0 - partial_frac))
                    px_surf = pygame.Surface((ps, ps), pygame.SRCALPHA)
                    px_surf.fill((*color, alpha))
                    surface.blit(px_surf, (ox + col_i * ps, oy + row_i * ps))
                else:
                    pygame.draw.rect(surface, color,
                                     (ox + col_i * ps, oy + row_i * ps, ps, ps))


def draw_flag_fall(surface, rect, sprite, colors, progress, pixels):
    num_cols = len(sprite[0])
    num_rows = len(sprite)
    ps = min(rect.width // (num_cols + 2), rect.height // (num_rows + 2))
    gw = num_cols * ps
    gh = num_rows * ps
    ox = rect.x + (rect.width - gw) // 2
    oy = rect.y + (rect.height - gh) // 2
    for p in pixels:
        if progress < p['delay']:
            pygame.draw.rect(surface, colors[p['ch']],
                             (ox + p['ci'] * ps, oy + p['ri'] * ps, ps, ps))
        else:
            t = min(1.0, (progress - p['delay']) / max(0.001, 1.0 - p['delay']))
            alpha = int(255 * (1.0 - t) ** 1.5)
            if alpha <= 0:
                continue
            dx = p['vx'] * t * ps * 2
            dy = p['vy'] * t * t * ps * 3
            s = pygame.Surface((ps, ps), pygame.SRCALPHA)
            s.fill((*colors[p['ch']], alpha))
            surface.blit(s, (ox + p['ci'] * ps + dx, oy + p['ri'] * ps + dy))


def draw_flag_flutter(surface, rect, sprite, colors, progress, pixels):
    num_cols = len(sprite[0])
    num_rows = len(sprite)
    ps = min(rect.width // (num_cols + 2), rect.height // (num_rows + 2))
    gw = num_cols * ps
    gh = num_rows * ps
    ox = rect.x + (rect.width - gw) // 2
    oy = rect.y + (rect.height - gh) // 2
    for p in pixels:
        if progress < p['delay']:
            pygame.draw.rect(surface, colors[p['ch']],
                             (ox + p['ci'] * ps, oy + p['ri'] * ps, ps, ps))
        else:
            t = min(1.0, (progress - p['delay']) / max(0.001, 1.0 - p['delay']))
            alpha = int(255 * (1.0 - t) ** 1.2)
            if alpha <= 0:
                continue
            dx = math.sin(t * p['wobble_freq'] * math.pi) * p['wobble_amp'] * ps
            dy = p['vy'] * t * ps * 3
            s = pygame.Surface((ps, ps), pygame.SRCALPHA)
            s.fill((*colors[p['ch']], alpha))
            surface.blit(s, (ox + p['ci'] * ps + dx, oy + p['ri'] * ps + dy))


def draw_mine(surface, rect):
    cx, cy = rect.centerx, rect.centery
    r = min(rect.width, rect.height) // 4
    pygame.draw.circle(surface, COL_BLACK, (cx, cy), r)
    spike_len = r + r // 2
    for angle in range(0, 360, 45):
        rad = math.radians(angle)
        ex = cx + int(math.cos(rad) * spike_len)
        ey = cy + int(math.sin(rad) * spike_len)
        pygame.draw.line(surface, COL_BLACK, (cx, cy), (ex, ey), 2)
        pygame.draw.circle(surface, COL_BLACK, (ex, ey), 2)
    highlight_size = max(r // 3, 2)
    pygame.draw.rect(surface, COL_WHITE,
                     (cx - r // 2, cy - r // 2, highlight_size, highlight_size))


def draw_mine_icon(surface, x, y, size=16):
    cx, cy = x + size // 2, y + size // 2
    r = size // 3
    pygame.draw.circle(surface, COL_WHITE, (cx, cy), r)
    for angle in range(0, 360, 45):
        rad = math.radians(angle)
        ex = cx + int(math.cos(rad) * (r + 2))
        ey = cy + int(math.sin(rad) * (r + 2))
        pygame.draw.line(surface, COL_WHITE, (cx, cy), (ex, ey), 1)


def draw_clock_icon(surface, x, y, size=16):
    cx, cy = x + size // 2, y + size // 2
    r = size // 2 - 1
    pygame.draw.circle(surface, COL_WHITE, (cx, cy), r, 1)
    pygame.draw.line(surface, COL_WHITE, (cx, cy), (cx, cy - r + 2), 1)
    pygame.draw.line(surface, COL_WHITE, (cx, cy), (cx + r - 3, cy), 1)


# --- Cell ---
class Cell:
    __slots__ = ('row', 'col', 'is_mine', 'is_revealed', 'is_flagged',
                 'adjacent_mines', 'anim_revealed')

    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.is_mine = False
        self.is_revealed = False
        self.is_flagged = False
        self.adjacent_mines = 0
        self.anim_revealed = False


# --- Game ---
class Game:
    def __init__(self):
        self.difficulty = "easy"
        self.theme_idx = 0
        self.all_sounds = {}
        for t in THEMES:
            self.all_sounds[t["id"]] = generate_sounds(t["id"])
        self._load_data()
        self.theme = THEMES[self.theme_idx]
        self.sounds = self.all_sounds[self.theme["id"]]
        self.new_best_timer = 0
        self.flag_anims = []
        self.flag_wipe_anims = {}
        self._theme_btn_rect = None
        self.new_game("easy")

    def new_game(self, difficulty):
        self.difficulty = difficulty
        self.cols, self.rows, self.mine_count = DIFFICULTIES[difficulty]
        self.grid = [[Cell(r, c) for c in range(self.cols)] for r in range(self.rows)]
        self.state = "ready"
        self.first_click = True
        self.timer_start = 0
        self.elapsed = 0
        self.flags_placed = 0
        self.hover_cell = None
        self.pressed = False
        self.mouse_pos = (0, 0)
        self.exploded_cell = None
        self.anim_state = None
        self.anim_timer = 0
        self.anim_layers = []
        self.anim_layer_idx = 0
        self.win_flash_timer = 0
        self.new_best_timer = 0
        self.flag_anims = []
        self.flag_wipe_anims = {}

    def _grid_offset(self):
        return (0, TOP_BAR_H)

    def window_size(self):
        w = self.cols * CELL_SIZE
        h = self.rows * CELL_SIZE + TOP_BAR_H + BOTTOM_BAR_H
        return (w, h)

    def cycle_theme(self):
        if self.state == "playing":
            return
        self.theme_idx = (self.theme_idx + 1) % len(THEMES)
        self.theme = THEMES[self.theme_idx]
        self.sounds = self.all_sounds[self.theme["id"]]
        self.sounds['click'].play()
        self._save_data()

    # --- Board Logic ---
    def place_mines(self, safe_r, safe_c):
        excluded = set()
        for dr in range(-1, 2):
            for dc in range(-1, 2):
                nr, nc = safe_r + dr, safe_c + dc
                if 0 <= nr < self.rows and 0 <= nc < self.cols:
                    excluded.add((nr, nc))

        candidates = [(r, c) for r in range(self.rows) for c in range(self.cols)
                      if (r, c) not in excluded]
        mines = random.sample(candidates, min(self.mine_count, len(candidates)))
        for r, c in mines:
            self.grid[r][c].is_mine = True

        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c].is_mine:
                    continue
                count = 0
                for dr in range(-1, 2):
                    for dc in range(-1, 2):
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < self.rows and 0 <= nc < self.cols:
                            if self.grid[nr][nc].is_mine:
                                count += 1
                self.grid[r][c].adjacent_mines = count

    def reveal(self, r, c):
        cell = self.grid[r][c]
        if cell.is_revealed or cell.is_flagged:
            return

        if self.first_click:
            self.first_click = False
            self.place_mines(r, c)
            self.timer_start = time.time()
            self.state = "playing"

        if cell.is_mine:
            self.state = "lost"
            cell.is_revealed = True
            self.exploded_cell = (r, c)
            self.sounds['explode'].play()
            self._start_lose_anim(r, c)
            return

        self.sounds['click'].play()
        queue = deque()
        cell.is_revealed = True
        if cell.adjacent_mines == 0:
            queue.append((r, c))

        while queue:
            cr, cc = queue.popleft()
            for dr in range(-1, 2):
                for dc in range(-1, 2):
                    nr, nc = cr + dr, cc + dc
                    if 0 <= nr < self.rows and 0 <= nc < self.cols:
                        neighbor = self.grid[nr][nc]
                        if not neighbor.is_revealed and not neighbor.is_mine and not neighbor.is_flagged:
                            neighbor.is_revealed = True
                            if neighbor.adjacent_mines == 0:
                                queue.append((nr, nc))

        if self._check_win():
            self.state = "won"
            self.flag_wipe_anims.clear()
            self.sounds['win'].play()
            self._start_win_anim()

    def toggle_flag(self, r, c):
        cell = self.grid[r][c]
        if cell.is_revealed:
            return
        if (r, c) in self.flag_wipe_anims:
            return
        if cell.is_flagged:
            self.flags_placed -= 1
            self.sounds['flag_remove'].play()
            theme_id = self.theme["id"]
            if theme_id == "midnight":
                self.flag_wipe_anims[(r, c)] = {
                    'start': pygame.time.get_ticks(),
                    'duration': 400,
                    'type': 'wipe',
                }
            elif theme_id == "autumn":
                sprite = self.theme["flag_sprite"]
                fcolors = self.theme["flag_colors"]
                pixels = []
                for ri, row in enumerate(sprite):
                    for ci, ch in enumerate(row):
                        if ch != '0' and ch in fcolors:
                            pixels.append({
                                'ri': ri, 'ci': ci, 'ch': ch,
                                'delay': ri / len(sprite) * 0.3 + random.uniform(0, 0.15),
                                'vx': random.uniform(-0.6, 0.6),
                                'vy': random.uniform(1.5, 3.0),
                            })
                self.flag_wipe_anims[(r, c)] = {
                    'start': pygame.time.get_ticks(),
                    'duration': 350,
                    'type': 'fall',
                    'pixels': pixels,
                }
            elif theme_id == "lavender":
                sprite = self.theme["flag_sprite"]
                fcolors = self.theme["flag_colors"]
                pixels = []
                for ri, row in enumerate(sprite):
                    for ci, ch in enumerate(row):
                        if ch != '0' and ch in fcolors:
                            pixels.append({
                                'ri': ri, 'ci': ci, 'ch': ch,
                                'delay': random.uniform(0, 0.25),
                                'vx': random.uniform(-0.5, 0.5),
                                'vy': random.uniform(-2.0, -1.2),
                                'wobble_freq': random.uniform(3, 6),
                                'wobble_amp': random.uniform(0.8, 1.5),
                            })
                self.flag_wipe_anims[(r, c)] = {
                    'start': pygame.time.get_ticks(),
                    'duration': 400,
                    'type': 'flutter',
                    'pixels': pixels,
                }
            else:
                cell.is_flagged = False
                self._create_flag_anim(r, c, False)
        else:
            cell.is_flagged = True
            self.flags_placed += 1
            self.sounds['flag_place'].play()
            self._create_flag_anim(r, c, True)

    def _check_win(self):
        for r in range(self.rows):
            for c in range(self.cols):
                cell = self.grid[r][c]
                if not cell.is_mine and not cell.is_revealed:
                    return False
        return True

    # --- Flag Animations ---
    def _create_flag_anim(self, r, c, placing):
        ox, oy = self._grid_offset()
        cx = ox + c * CELL_SIZE + CELL_SIZE // 2
        cy = oy + r * CELL_SIZE + CELL_SIZE // 2
        theme_id = self.theme["id"]

        if theme_id == "classic":
            return

        anim = {
            'start': pygame.time.get_ticks(),
            'duration': 400,
            'theme': theme_id,
            'cx': cx, 'cy': cy,
            'placing': placing,
            'particles': [],
        }

        if theme_id == 'autumn':
            for _ in range(5):
                dy = 1 if placing else -1
                anim['particles'].append({
                    'x': float(cx + random.randint(-10, 10)),
                    'y': float(cy + random.randint(-5, 5)),
                    'vx': random.uniform(-0.4, 0.4),
                    'vy': random.uniform(0.5, 1.5) * dy,
                    'color': random.choice([(0xE8, 0x7A, 0x20), (0x8B, 0x45, 0x13), (0xCC, 0x66, 0x00)]),
                    'size': random.randint(2, 4),
                })
        elif theme_id == 'lavender':
            for _ in range(6):
                dy = -1 if placing else 1
                anim['particles'].append({
                    'x': float(cx + random.randint(-8, 8)),
                    'y': float(cy + random.randint(-5, 5)),
                    'vx': random.uniform(-0.6, 0.6),
                    'vy': random.uniform(0.4, 1.4) * dy,
                    'wobble': random.uniform(0, 6.28),
                    'color': random.choice([(0xBB, 0x88, 0xDD), (0xDD, 0xAA, 0xFF), (0xFF, 0xCC, 0xFF)]),
                    'size': random.randint(2, 3),
                })

        self.flag_anims.append(anim)

    def _draw_flag_anims(self, screen):
        now = pygame.time.get_ticks()
        alive = []
        for anim in self.flag_anims:
            elapsed = now - anim['start']
            if elapsed > anim['duration']:
                continue
            alive.append(anim)
            progress = elapsed / anim['duration']

            if anim['theme'] == 'autumn':
                for p in anim['particles']:
                    px = p['x'] + p['vx'] * elapsed * 0.06
                    py = p['y'] + p['vy'] * elapsed * 0.06
                    size = max(1, int(p['size'] * (1 - progress)))
                    pygame.draw.rect(screen, p['color'], (int(px), int(py), size, size))

            elif anim['theme'] == 'midnight':
                cell_x = anim['cx'] - CELL_SIZE // 2
                cell_y = anim['cy'] - CELL_SIZE // 2
                sweep_x = cell_x + int(CELL_SIZE * progress)
                shadow_w = max(1, int(CELL_SIZE * 0.3))
                shadow = pygame.Surface((shadow_w, CELL_SIZE), pygame.SRCALPHA)
                alpha = int(100 * (1 - progress))
                shadow.fill((0, 0, 20, alpha))
                screen.blit(shadow, (sweep_x - shadow_w // 2, cell_y))

            elif anim['theme'] == 'lavender':
                for p in anim['particles']:
                    px = p['x'] + p['vx'] * elapsed * 0.06 + math.sin(elapsed * 0.015 + p['wobble']) * 3
                    py = p['y'] + p['vy'] * elapsed * 0.06
                    size = max(1, int(p['size'] * (1 - progress * 0.5)))
                    pygame.draw.rect(screen, p['color'], (int(px), int(py), size, size))

        self.flag_anims = alive

    # --- Animations ---
    def _start_lose_anim(self, sr, sc):
        layers = []
        visited = set()
        visited.add((sr, sc))
        current_layer = [(sr, sc)]
        while current_layer:
            next_layer = []
            mine_layer = []
            for r, c in current_layer:
                if self.grid[r][c].is_mine and (r, c) != (sr, sc):
                    mine_layer.append((r, c))
                for dr in range(-1, 2):
                    for dc in range(-1, 2):
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < self.rows and 0 <= nc < self.cols and (nr, nc) not in visited:
                            visited.add((nr, nc))
                            next_layer.append((nr, nc))
            if mine_layer:
                layers.append(mine_layer)
            current_layer = next_layer
        self.anim_layers = layers
        self.anim_layer_idx = 0
        self.anim_timer = pygame.time.get_ticks()
        self.anim_state = "lose"

    def _start_win_anim(self):
        self.anim_state = "win"
        self.win_flash_timer = pygame.time.get_ticks()
        for r in range(self.rows):
            for c in range(self.cols):
                cell = self.grid[r][c]
                if cell.is_mine and not cell.is_flagged:
                    cell.is_flagged = True
                    self.flags_placed += 1
        elapsed = self.elapsed
        best = self.best_times.get(self.difficulty)
        if best is None or elapsed < best:
            self.best_times[self.difficulty] = elapsed
            self._save_data()
            self.new_best_timer = pygame.time.get_ticks()

    def update(self):
        if self.state == "playing":
            self.elapsed = int(time.time() - self.timer_start)

        if self.anim_state == "lose":
            now = pygame.time.get_ticks()
            if self.anim_layer_idx < len(self.anim_layers):
                if now - self.anim_timer > 50:
                    for r, c in self.anim_layers[self.anim_layer_idx]:
                        self.grid[r][c].anim_revealed = True
                    self.anim_layer_idx += 1
                    self.anim_timer = now
            else:
                self.anim_state = "lose_done"

        if self.flag_wipe_anims:
            now = pygame.time.get_ticks()
            completed = []
            for key, anim in self.flag_wipe_anims.items():
                if now - anim['start'] >= anim['duration']:
                    completed.append(key)
            for key in completed:
                r, c = key
                self.grid[r][c].is_flagged = False
                del self.flag_wipe_anims[key]

    # --- Persistence ---
    def _load_data(self):
        self.best_times = {}
        try:
            with open(SCORES_FILE, 'r') as f:
                data = json.load(f)
                if isinstance(data, dict) and "best_times" in data:
                    self.theme_idx = data.get("theme", 0) % len(THEMES)
                    self.best_times = data["best_times"]
                elif isinstance(data, dict):
                    self.best_times = data
        except (FileNotFoundError, json.JSONDecodeError):
            pass

    def _save_data(self):
        with open(SCORES_FILE, 'w') as f:
            json.dump({"best_times": self.best_times, "theme": self.theme_idx}, f)

    # --- Input ---
    def pos_to_cell(self, pos):
        ox, oy = self._grid_offset()
        gx, gy = pos[0] - ox, pos[1] - oy
        if gx < 0 or gy < 0:
            return None
        c = gx // CELL_SIZE
        r = gy // CELL_SIZE
        if 0 <= r < self.rows and 0 <= c < self.cols:
            return (r, c)
        return None

    def handle_click(self, pos, button):
        if self.state in ("won", "lost"):
            return
        if self.anim_state == "lose":
            return

        cell_pos = self.pos_to_cell(pos)
        if cell_pos is None:
            return

        r, c = cell_pos
        if button == 1:
            self.reveal(r, c)
        elif button == 3:
            if self.state in ("ready", "playing"):
                self.toggle_flag(r, c)

    def _handle_ui_click(self, pos):
        x, y = pos
        if getattr(self, '_play_again_rect', None):
            px, py, pw, ph = self._play_again_rect
            if px <= x <= px + pw and py <= y <= py + ph:
                self.sounds['click'].play()
                self.new_game(self.difficulty)
                return True
        for bx, by, bw, bh, diff in getattr(self, '_btn_rects', []):
            if bx <= x <= bx + bw and by <= y <= by + bh:
                self.sounds[f'btn_{diff}'].play()
                self.new_game(diff)
                return True
        if self._theme_btn_rect:
            tx, ty, tw, th = self._theme_btn_rect
            if tx <= x <= tx + tw and ty <= y <= ty + th:
                self.cycle_theme()
                return True
        return False

    # --- Drawing ---
    def draw(self, screen):
        screen.fill(self.theme["bg"])
        self._draw_top_bar(screen)
        self._draw_grid(screen)
        self._draw_flag_anims(screen)
        self._draw_bottom_bar(screen)
        self._draw_overlay(screen)

    def _draw_top_bar(self, screen):
        t = self.theme
        w = self.cols * CELL_SIZE
        pygame.draw.rect(screen, t["top_bar"], (0, 0, w, TOP_BAR_H))

        remaining = self.mine_count - self.flags_placed
        mine_text = f"{remaining:03d}" if remaining >= 0 else f"-{abs(remaining):02d}"
        mine_surf = render_pixel_text(mine_text, COL_WHITE, 3)
        draw_mine_icon(screen, 10, (TOP_BAR_H - 16) // 2, 16)
        screen.blit(mine_surf, (32, (TOP_BAR_H - mine_surf.get_height()) // 2))

        counter_end = 32 + mine_surf.get_width() + 8

        timer_val = min(self.elapsed, 9999)
        timer_text = f"{timer_val:04d}"
        timer_surf = render_pixel_text(timer_text, COL_WHITE, 3)
        timer_x = w - timer_surf.get_width() - 12
        draw_clock_icon(screen, timer_x - 22, (TOP_BAR_H - 16) // 2, 16)
        screen.blit(timer_surf, (timer_x, (TOP_BAR_H - timer_surf.get_height()) // 2))

        timer_start = timer_x - 22 - 8

        btn_h = 30
        gap = 6
        avail = timer_start - counter_end
        btn_w = (avail - 2 * gap) // 3
        btn_w = max(btn_w, 50)
        start_x = counter_end + (avail - 3 * btn_w - 2 * gap) // 2
        btn_y = (TOP_BAR_H - btn_h) // 2
        diffs = ["easy", "medium", "expert"]
        labels = ["EASY", "MED", "EXPERT"]
        self._btn_rects = []
        for i, (diff, label) in enumerate(zip(diffs, labels)):
            bx = start_x + i * (btn_w + gap)
            is_active = diff == self.difficulty
            bg = t["button_active"] if is_active else t["button_bg"]
            pygame.draw.rect(screen, bg, (bx, btn_y, btn_w, btn_h), border_radius=4)
            border_col = t["border_light"] if is_active else t["grid_line"]
            pygame.draw.rect(screen, border_col, (bx, btn_y, btn_w, btn_h), 2, border_radius=4)
            txt_col = COL_BLACK if is_active else t["button_text"]
            txt = render_pixel_text(label, txt_col, 2)
            screen.blit(txt, (bx + (btn_w - txt.get_width()) // 2,
                              btn_y + (btn_h - txt.get_height()) // 2))
            self._btn_rects.append((bx, btn_y, btn_w, btn_h, diff))

    def _draw_grid(self, screen):
        t = self.theme
        ox, oy = self._grid_offset()
        hover = self.pos_to_cell(self.mouse_pos)
        sprite = t["flag_sprite"]
        fcolors = t["flag_colors"]
        for r in range(self.rows):
            for c in range(self.cols):
                cell = self.grid[r][c]
                x = ox + c * CELL_SIZE
                y = oy + r * CELL_SIZE
                rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)

                if cell.is_revealed or cell.anim_revealed:
                    if cell.is_mine:
                        is_exploded = self.exploded_cell == (r, c)
                        bg = t["exploded"] if is_exploded else t["revealed"]
                        pygame.draw.rect(screen, bg, rect)
                        draw_mine(screen, rect)
                    else:
                        pygame.draw.rect(screen, t["revealed"], rect)
                        if cell.adjacent_mines > 0:
                            num_surf = render_pixel_text(
                                str(cell.adjacent_mines),
                                t["num_colors"][cell.adjacent_mines], 4)
                            screen.blit(num_surf,
                                        (x + (CELL_SIZE - num_surf.get_width()) // 2,
                                         y + (CELL_SIZE - num_surf.get_height()) // 2))
                elif cell.is_flagged:
                    if self.state == "lost" and not cell.is_mine:
                        pygame.draw.rect(screen, t["revealed"], rect)
                        draw_flag(screen, rect, sprite, fcolors)
                        xc = t["flag_x_color"]
                        pygame.draw.line(screen, xc,
                                         (x + 6, y + 6), (x + CELL_SIZE - 6, y + CELL_SIZE - 6), 3)
                        pygame.draw.line(screen, xc,
                                         (x + CELL_SIZE - 6, y + 6), (x + 6, y + CELL_SIZE - 6), 3)
                    else:
                        self._draw_raised_cell(screen, rect, t["unrevealed"])
                        if (r, c) in self.flag_wipe_anims:
                            anim = self.flag_wipe_anims[(r, c)]
                            elapsed = pygame.time.get_ticks() - anim['start']
                            progress = min(1.0, elapsed / anim['duration'])
                            anim_type = anim.get('type', 'wipe')
                            if anim_type == 'fall':
                                draw_flag_fall(screen, rect, sprite, fcolors, progress, anim['pixels'])
                            elif anim_type == 'flutter':
                                draw_flag_flutter(screen, rect, sprite, fcolors, progress, anim['pixels'])
                            else:
                                draw_flag_wiped(screen, rect, sprite, fcolors, progress)
                                bar_w = max(1, int(CELL_SIZE * 0.3))
                                bar_x = rect.x + int(CELL_SIZE * (1 - progress)) - bar_w // 2
                                bar_alpha = int(100 * (1 - progress))
                                bar_surf = pygame.Surface((bar_w, CELL_SIZE), pygame.SRCALPHA)
                                bar_surf.fill((0, 0, 20, bar_alpha))
                                screen.blit(bar_surf, (bar_x, rect.y))
                        else:
                            draw_flag(screen, rect, sprite, fcolors)
                else:
                    is_hover = hover == (r, c)
                    is_pressed = is_hover and self.pressed
                    if is_pressed:
                        self._draw_pressed_cell(screen, rect)
                    elif is_hover and self.state in ("ready", "playing"):
                        self._draw_raised_cell(screen, rect, t["hover"])
                    else:
                        if self.anim_state == "win" and self.state == "won":
                            elapsed_ms = pygame.time.get_ticks() - self.win_flash_timer
                            if elapsed_ms < 400 and (elapsed_ms // 100) % 2 == 0:
                                self._draw_raised_cell(screen, rect, t["win_flash"])
                            else:
                                self._draw_raised_cell(screen, rect, t["unrevealed"])
                        else:
                            self._draw_raised_cell(screen, rect, t["unrevealed"])

                pygame.draw.rect(screen, t["grid_line"], rect, 1)

    def _draw_raised_cell(self, screen, rect, base_color):
        t = self.theme
        pygame.draw.rect(screen, base_color, rect)
        x, y, w, h = rect
        for i in range(BORDER_W):
            pygame.draw.line(screen, t["border_light"], (x + i, y + i), (x + w - 1 - i, y + i))
            pygame.draw.line(screen, t["border_light"], (x + i, y + i), (x + i, y + h - 1 - i))
        for i in range(BORDER_W):
            pygame.draw.line(screen, t["border_dark"], (x + i, y + h - 1 - i), (x + w - 1 - i, y + h - 1 - i))
            pygame.draw.line(screen, t["border_dark"], (x + w - 1 - i, y + i), (x + w - 1 - i, y + h - 1 - i))

    def _draw_pressed_cell(self, screen, rect):
        t = self.theme
        pygame.draw.rect(screen, t["pressed"], rect)
        x, y, w, h = rect
        for i in range(BORDER_W):
            pygame.draw.line(screen, t["border_dark"], (x + i, y + i), (x + w - 1 - i, y + i))
            pygame.draw.line(screen, t["border_dark"], (x + i, y + i), (x + i, y + h - 1 - i))
        for i in range(BORDER_W):
            pygame.draw.line(screen, t["border_light"], (x + i, y + h - 1 - i), (x + w - 1 - i, y + h - 1 - i))
            pygame.draw.line(screen, t["border_light"], (x + w - 1 - i, y + i), (x + w - 1 - i, y + h - 1 - i))

    def _draw_bottom_bar(self, screen):
        t = self.theme
        w = self.cols * CELL_SIZE
        bar_y = TOP_BAR_H + self.rows * CELL_SIZE
        pygame.draw.rect(screen, t["top_bar"], (0, bar_y, w, BOTTOM_BAR_H))

        best = self.best_times.get(self.difficulty)
        if best is not None:
            txt = render_pixel_text(f"BEST: {best}S", COL_WHITE, 2)
        else:
            txt = render_pixel_text("BEST: ---", COL_WHITE, 2)
        screen.blit(txt, (8, bar_y + (BOTTOM_BAR_H - txt.get_height()) // 2))

        can_switch = self.state != "playing"
        theme_label = t["name"] + " >"
        label_color = COL_WHITE if can_switch else (100, 100, 100)
        theme_txt = render_pixel_text(theme_label, label_color, 2)
        btn_w = theme_txt.get_width() + 12
        btn_h = 22
        btn_x = w - btn_w - 6
        btn_y = bar_y + (BOTTOM_BAR_H - btn_h) // 2

        btn_bg = t["button_bg"] if can_switch else t["top_bar"]
        pygame.draw.rect(screen, btn_bg, (btn_x, btn_y, btn_w, btn_h), border_radius=3)
        border = t["grid_line"] if can_switch else (70, 70, 70)
        pygame.draw.rect(screen, border, (btn_x, btn_y, btn_w, btn_h), 1, border_radius=3)
        screen.blit(theme_txt, (btn_x + 6, btn_y + (btn_h - theme_txt.get_height()) // 2))
        self._theme_btn_rect = (btn_x, btn_y, btn_w, btn_h)

    def _draw_play_again(self, screen, center_y):
        t = self.theme
        w = self.cols * CELL_SIZE
        btn_txt = render_pixel_text("PLAY AGAIN", COL_WHITE, 3)
        btn_w = btn_txt.get_width() + 30
        btn_h = btn_txt.get_height() + 16
        btn_x = (w - btn_w) // 2
        btn_y = center_y
        pygame.draw.rect(screen, t["button_bg"], (btn_x, btn_y, btn_w, btn_h), border_radius=5)
        pygame.draw.rect(screen, t["border_light"], (btn_x, btn_y, btn_w, btn_h), 2, border_radius=5)
        screen.blit(btn_txt, (btn_x + 15, btn_y + 8))
        self._play_again_rect = (btn_x, btn_y, btn_w, btn_h)

    def _draw_overlay(self, screen):
        t = self.theme
        w = self.cols * CELL_SIZE
        h = self.rows * CELL_SIZE
        self._play_again_rect = None

        if self.state == "won" and self.anim_state == "win":
            elapsed_ms = pygame.time.get_ticks() - self.win_flash_timer
            if elapsed_ms > 600:
                overlay = pygame.Surface((w, h), pygame.SRCALPHA)
                overlay.fill(COL_OVERLAY)
                screen.blit(overlay, (0, TOP_BAR_H))

                win_text = render_pixel_text("YOU WIN!", COL_WHITE, 5)
                text_y = TOP_BAR_H + (h - win_text.get_height()) // 2 - 30
                screen.blit(win_text, ((w - win_text.get_width()) // 2, text_y))

                if self.new_best_timer > 0:
                    best_text = render_pixel_text("NEW BEST!", (0xFF, 0xD7, 0x00), 4)
                    screen.blit(best_text,
                                ((w - best_text.get_width()) // 2,
                                 text_y + win_text.get_height() + 6))
                    self._draw_play_again(screen, text_y + win_text.get_height() + best_text.get_height() + 20)
                else:
                    self._draw_play_again(screen, text_y + win_text.get_height() + 16)

        if self.state == "lost" and self.anim_state == "lose_done":
            overlay = pygame.Surface((w, h), pygame.SRCALPHA)
            overlay.fill(COL_OVERLAY)
            screen.blit(overlay, (0, TOP_BAR_H))
            lose_text = render_pixel_text("GAME OVER", t["flag_x_color"], 5)
            text_y = TOP_BAR_H + (h - lose_text.get_height()) // 2 - 20
            screen.blit(lose_text, ((w - lose_text.get_width()) // 2, text_y))
            self._draw_play_again(screen, text_y + lose_text.get_height() + 16)

        if self.new_best_timer > 0 and self.state != "won":
            elapsed_ms = pygame.time.get_ticks() - self.new_best_timer
            if elapsed_ms > 3000:
                self.new_best_timer = 0


# --- Main ---
def main():
    pygame.init()
    pygame.mixer.init(22050, -16, 1, 512)

    game = Game()
    w, h = game.window_size()
    screen = pygame.display.set_mode((w, h))
    pygame.display.set_caption("Minesweeper")

    clock = pygame.time.Clock()
    running = True
    ui_clicked = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    game.pressed = True
                    game.mouse_pos = event.pos
                    ui_clicked = game._handle_ui_click(event.pos)
                    if ui_clicked:
                        game.pressed = False
                        w, h = game.window_size()
                        screen = pygame.display.set_mode((w, h))
                elif event.button == 3:
                    game.handle_click(event.pos, 3)
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    game.pressed = False
                    if not ui_clicked:
                        game.handle_click(event.pos, 1)
                    ui_clicked = False
            elif event.type == pygame.MOUSEMOTION:
                game.mouse_pos = event.pos

        game.update()
        game.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
