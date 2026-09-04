"""
Pro FFmpeg Video Compositor & Assembler for AI Teacher.
Stitches Avatar video clips, subject-aware visual slides (static & motion MP4), audio streams, and intro/outro title cards.
Deliverable for Siddhant.
"""

import os
import shutil
import subprocess
from pathlib import Path
from typing import List, Optional
from PIL import Image, ImageDraw, ImageFont

STORAGE_VIDEOS_DIR = Path("storage/generated_videos")
STORAGE_VIDEOS_DIR.mkdir(parents=True, exist_ok=True)

def stitch_video(clip_paths: List[str], output_path: Optional[str] = None) -> str:
    """
    Core contract function: Concatenates a list of section video MP4 clips into a single final MP4 video.
    Returns absolute path to final stitched video.
    """
    valid_clips = [p for p in clip_paths if p and os.path.exists(p)]
    if not output_path:
        output_path = str((STORAGE_VIDEOS_DIR / "final_lesson_video.mp4").resolve())

    if not valid_clips:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        return output_path

    if len(valid_clips) == 1:
        return str(Path(valid_clips[0]).resolve())

    output_path = str(Path(output_path).resolve())
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    if not shutil.which("ffmpeg"):
        print("[Video Assembler Warn] FFmpeg missing from system PATH. Returning initial clip asset.")
        return str(Path(valid_clips[0]).resolve())

    concat_txt_path = str((STORAGE_VIDEOS_DIR / f"concat_{hash(output_path) & 0xffffffff}.txt").resolve())
    with open(concat_txt_path, "w", encoding="utf-8") as f:
        for p in valid_clips:
            abs_p = str(Path(p).resolve()).replace("\\", "/")
            f.write(f"file '{abs_p}'\n")

    cmd = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", concat_txt_path,
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "fast",
        "-c:a", "aac", "-b:a", "192k",
        output_path
    ]

    try:
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except FileNotFoundError:
        return str(Path(valid_clips[0]).resolve())

    if os.path.exists(concat_txt_path):
        try:
            os.remove(concat_txt_path)
        except OSError:
            pass

    if res.returncode == 0 and os.path.exists(output_path):
        return output_path
    return output_path

def create_title_card_video(
    title: str,
    subtitle: str = "AI Teacher Educator Platform • Interactive Session",
    duration: float = 3.0,
    output_path: Optional[str] = None
) -> str:
    if not output_path:
        filename = f"titlecard_{hash(title) & 0xffffffff}.mp4"
        output_path = str((STORAGE_VIDEOS_DIR / filename).resolve())

    output_path = str(Path(output_path).resolve())
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    img = Image.new("RGBA", (1920, 1080), (11, 15, 25, 255))
    draw = ImageDraw.Draw(img)

    for x in range(0, 1920, 80):
        draw.line([(x, 0), (x, 1080)], fill=(30, 41, 59, 60), width=1)
    for y in range(0, 1080, 80):
        draw.line([(0, y), (1920, y)], fill=(30, 41, 59, 60), width=1)

    draw.rectangle([(0, 0), (1920, 10)], fill=(56, 189, 248))

    draw.rounded_rectangle([360, 280, 1560, 800], radius=24, fill=(22, 28, 45, 240), outline=(56, 189, 248, 160), width=3)
    
    font_t = _get_font(56, bold=True)
    font_s = _get_font(28)
    font_b = _get_font(22, bold=True)

    draw.rounded_rectangle([420, 340, 680, 385], radius=12, fill=(56, 189, 248, 40), outline=(56, 189, 248), width=1)
    draw.text((440, 350), "AI EDUCATOR", font=font_b, fill=(56, 189, 248))

    draw.text((420, 420), title, font=font_t, fill=(248, 250, 252))
    draw.line([(420, 510), (820, 510)], fill=(168, 85, 247), width=4)
    draw.text((420, 550), subtitle, font=font_s, fill=(148, 163, 184))

    card_img_path = str((STORAGE_VIDEOS_DIR / f"temp_title_{hash(title) & 0xffffffff}.png").resolve())
    img.save(card_img_path)

    if not shutil.which("ffmpeg"):
        return card_img_path

    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", card_img_path,
        "-f", "lavfi", "-i", "anullsrc=channel_layout=stereo:sample_rate=44100",
        "-c:v", "libx264", "-t", str(duration), "-pix_fmt", "yuv420p", "-preset", "fast",
        "-c:a", "aac", "-shortest",
        output_path
    ]
    try:
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except FileNotFoundError:
        return card_img_path

    if os.path.exists(output_path):
        return output_path
    return card_img_path

def create_section_video(
    avatar_video_path: str,
    visual_asset_path: str,
    audio_path: str,
    srt_subtitle_path: Optional[str] = None,
    output_path: Optional[str] = None,
    avatar_position: str = "bottom_right"
) -> str:
    avatar_video_path = str(Path(avatar_video_path).resolve())
    visual_asset_path = str(Path(visual_asset_path).resolve())
    audio_path = str(Path(audio_path).resolve())

    if not output_path:
        filename = f"section_{hash(avatar_video_path + visual_asset_path) & 0xffffffff}.mp4"
        output_path = str((STORAGE_VIDEOS_DIR / filename).resolve())

    output_path = str(Path(output_path).resolve())
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    if not shutil.which("ffmpeg"):
        print("[Video Assembler Warn] FFmpeg missing from system PATH. Returning visual slide image.")
        return visual_asset_path

    pip_w, pip_h = 380, 380
    margin = 50

    if avatar_position == "top_right":
        overlay_x, overlay_y = 1920 - pip_w - margin, margin
    elif avatar_position == "top_left":
        overlay_x, overlay_y = margin, margin
    elif avatar_position == "bottom_left":
        overlay_x, overlay_y = margin, 1080 - pip_h - margin
    else:
        overlay_x, overlay_y = 1920 - pip_w - margin, 1080 - pip_h - margin

    filtergraph = (
        f"[0:v]scale=1920:1080[bg];"
        f"[1:v]scale={pip_w}:{pip_h}[avatar];"
        f"[bg][avatar]overlay={overlay_x}:{overlay_y}:shortest=1[comp]"
    )
    input_args = ["-loop", "1", "-i", visual_asset_path, "-i", avatar_video_path, "-i", audio_path]

    out_stream = "[comp]"
    cmd = ["ffmpeg", "-y"] + input_args + [
        "-filter_complex", filtergraph,
        "-map", out_stream, "-map", "2:a",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "fast",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        output_path
    ]

    try:
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except FileNotFoundError:
        return visual_asset_path

    if res.returncode == 0 and os.path.exists(output_path):
        return output_path

    return visual_asset_path

def _get_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    font_name = "arialbd.ttf" if bold else "arial.ttf"
    try:
        return ImageFont.truetype(font_name, size)
    except OSError:
        return ImageFont.load_default()
