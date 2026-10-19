"""MIDI + visual helpers for the SoundCraft hands-in demo."""

from __future__ import annotations

import struct
import wave
from pathlib import Path

from PIL import Image, ImageDraw

PPQ = 480
BPM = 112
EIGHTH = PPQ // 2

# [pitch, start_eighth, length_eighths]
MELODY: list[tuple[int, int, int]] = [
    (60, 0, 2),
    (63, 2, 1),
    (67, 3, 1),
    (70, 4, 2),
    (72, 6, 2),
    (70, 8, 1),
    (67, 9, 1),
    (63, 10, 2),
    (60, 12, 4),
    (67, 16, 2),
    (72, 18, 2),
    (75, 20, 2),
    (72, 22, 2),
    (70, 24, 2),
    (67, 26, 2),
    (63, 28, 4),
]


def _vlq(value: int) -> bytes:
    out = [value & 0x7F]
    value >>= 7
    while value:
        out.append((value & 0x7F) | 0x80)
        value >>= 7
    return bytes(reversed(out))


def write_melody(path: Path) -> int:
    events: list[tuple[int, int, bytes]] = []
    micros = int(60_000_000 / BPM)
    events.append((0, 0, b"\xff\x51\x03" + micros.to_bytes(3, "big")))
    events.append((0, 1, b"\xff\x58\x04\x04\x02\x18\x08"))
    events.append((0, 2, b"\xc0\x00"))
    for pitch, start, length in MELODY:
        on = start * EIGHTH
        off = on + length * EIGHTH
        events.append((on, 3, bytes([0x90, pitch, 100])))
        events.append((off, 2, bytes([0x80, pitch, 64])))
    events.sort(key=lambda event: (event[0], event[1]))
    data = bytearray()
    last = 0
    for tick, _order, payload in events:
        data += _vlq(tick - last) + payload
        last = tick
    data += _vlq(0) + b"\xff\x2f\x00"
    track = b"MTrk" + struct.pack(">I", len(data)) + bytes(data)
    header = b"MThd" + struct.pack(">IHHH", 6, 0, 1, PPQ)
    path.write_bytes(header + track)
    return len(MELODY)


def render_waveform(wav_path: Path, png_path: Path) -> None:
    with wave.open(str(wav_path), "rb") as fh:
        channels = fh.getnchannels()
        width = fh.getsampwidth()
        frames = fh.readframes(fh.getnframes())
    step = max(1, width * channels)
    samples: list[int] = []
    for offset in range(0, len(frames), step):
        chunk = frames[offset : offset + width]
        if len(chunk) == width:
            samples.append(int.from_bytes(chunk, "little", signed=True))
    if not samples:
        samples = [0]
    height, img_w = 260, 1000
    mid = height // 2
    per_col = max(1, len(samples) // img_w)
    image = Image.new("RGB", (img_w, height), "#0b1220")
    draw = ImageDraw.Draw(image)
    draw.line([(0, mid), (img_w, mid)], fill="#1c3450")
    peak = max(1, max(abs(s) for s in samples))
    for x in range(img_w):
        chunk = samples[x * per_col : (x + 1) * per_col] or [0]
        amp = int((max(abs(v) for v in chunk) / peak) * (mid - 10))
        draw.line([(x, mid - amp), (x, mid + amp)], fill="#ffd27a")
    image.save(png_path)


def render_piano_roll(png_path: Path) -> None:
    width, height = 1000, 260
    lo, hi = 58, 78
    image = Image.new("RGB", (width, height), "#0b1220")
    draw = ImageDraw.Draw(image)
    for pitch in range(lo, hi + 1):
        y = height - int((pitch - lo) / (hi - lo) * (height - 20)) - 10
        draw.line([(0, y + 6), (width, y + 6)], fill="#122033")
    total = 32
    for pitch, start, length in MELODY:
        x0 = int(start / total * width)
        x1 = int((start + length) / total * width)
        y = height - int((pitch - lo) / (hi - lo) * (height - 20)) - 10
        draw.rounded_rectangle([x0 + 1, y, x1 - 1, y + 12], radius=2, fill="#7cc7ff")
    image.save(png_path)
