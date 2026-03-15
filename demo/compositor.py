"""Frame-by-frame compositor: read GIF frames, apply camera crop, encode to MP4.

Replaces the broken ffmpeg-expression approach. Camera interpolation happens
in Python (PIL crop) where we have full control, then raw frames are piped
to ffmpeg for encoding.
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import List

from PIL import Image

from demo.camera import CameraKeyframe, interpolate_keyframes


def composite_frames(
    gif_path: Path,
    output_path: Path,
    keyframes: List[CameraKeyframe],
    output_w: int,
    output_h: int,
    fps: int = 30,
) -> None:
    """Read GIF frames, apply camera crop per-frame, encode to MP4.

    Streams frames through ffmpeg via stdin pipe — memory usage is O(1 frame).
    """
    # Ensure even dimensions for H.264
    output_w &= ~1
    output_h &= ~1

    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-f", "rawvideo",
        "-pix_fmt", "rgb24",
        "-s", f"{output_w}x{output_h}",
        "-r", str(fps),
        "-i", "pipe:0",
        "-c:v", "libx264",
        "-preset", "slow",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        str(output_path),
    ]

    proc = subprocess.Popen(
        ffmpeg_cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    _process_gif(proc, gif_path, keyframes, output_w, output_h, fps)
    proc.stdin.close()
    proc.wait()

    if proc.returncode != 0:
        stderr = proc.stderr.read() if proc.stderr else b""
        raise RuntimeError(
            f"ffmpeg encoding failed (exit {proc.returncode}):\n"
            f"{stderr.decode(errors='replace')}"
        )


def _process_gif(
    proc: subprocess.Popen,
    gif_path: Path,
    keyframes: List[CameraKeyframe],
    output_w: int,
    output_h: int,
    fps: int,
) -> None:
    """Iterate GIF frames, crop, and write to ffmpeg stdin."""
    img = Image.open(gif_path)
    t = 0.0

    while True:
        frame = img.copy().convert("RGB")
        duration_ms = img.info.get("duration", 33)  # fallback ~30fps

        # Apply camera: interpolate keyframes at this timestamp
        zoom, cx, cy = interpolate_keyframes(keyframes, t)
        cropped = _apply_camera(frame, zoom, cx, cy, output_w, output_h)

        # Write this frame enough times to match its display duration at target fps
        n_repeats = max(1, round(duration_ms / 1000.0 * fps))
        raw = cropped.tobytes()
        for _ in range(n_repeats):
            proc.stdin.write(raw)

        t += duration_ms / 1000.0

        try:
            img.seek(img.tell() + 1)
        except EOFError:
            break


def _apply_camera(
    frame: Image.Image,
    zoom: float,
    cx: float,
    cy: float,
    output_w: int,
    output_h: int,
) -> Image.Image:
    """Crop and scale a single frame based on camera state."""
    input_w, input_h = frame.size

    crop_w = input_w / zoom
    crop_h = input_h / zoom

    # Center the crop on (cx, cy) in normalized coordinates
    crop_x = cx * input_w - crop_w / 2
    crop_y = cy * input_h - crop_h / 2

    # Clamp to image bounds
    crop_x = max(0, min(crop_x, input_w - crop_w))
    crop_y = max(0, min(crop_y, input_h - crop_h))

    cropped = frame.crop((
        int(crop_x),
        int(crop_y),
        int(crop_x + crop_w),
        int(crop_y + crop_h),
    ))

    return cropped.resize((output_w, output_h), Image.LANCZOS)
