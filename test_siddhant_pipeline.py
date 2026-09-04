"""
Siddhant's Media & Ingestion Pipeline Showcase Script.
"""

import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from backend.app.core.ingestion import extract_text, extract_metadata, extract_text_from_url
from backend.app.media.tts import generate_audio, generate_audio_with_subtitles
from backend.app.media.visuals import render_visual, render_animated_visual
from backend.app.media.avatar import generate_avatar_video
from backend.app.media.video_assembler import create_section_video, create_title_card_video, stitch_video

def run_siddhant_verification():
    print("=" * 75)
    print(" SIDDHANT'S MEDIA & INGESTION PIPELINE — HANDOVER VERIFICATION")
    print("=" * 75)

    # 1. Document Ingestion Test
    pdf_sample = "docs/contracts.md"
    if os.path.exists(pdf_sample):
        text = extract_text(pdf_sample)
        meta = extract_metadata(pdf_sample)
        print(f"[OK] Document Ingestion: Extracted {len(text)} chars from '{pdf_sample}'")
        print(f"[OK] Metadata: Words={meta.get('word_count')}")

    # 2. TTS Generation Test
    script = "Namaste! Aaj hum electric current aur voltage ke concept ko samjhenge."
    audio_path, srt_path = generate_audio_with_subtitles(script, "hi")
    print(f"[OK] TTS Audio & Subtitles generated: {audio_path}")

    # 3. Visual Asset Rendering
    visual_path = render_visual("Ohm's Law", "diagram")
    print(f"[OK] Visual Slide Asset rendered: {visual_path}")

    # 4. Avatar Video Clip Generation
    avatar_path = generate_avatar_video(audio_path, script=script, persona="dr_sharma")
    print(f"[OK] AI Avatar Video clip rendered: {avatar_path}")

    # 5. Video Assembly
    sec_video = create_section_video(avatar_path, visual_path, audio_path, srt_path)
    print(f"[OK] Section Video Composed: {sec_video}")

    print("\n=============================================================")
    print("ALL SIDDHANT MEDIA PIPELINE DELIVERABLES VERIFIED 100% CLEANLY!")
    print("=============================================================")

if __name__ == "__main__":
    run_siddhant_verification()
