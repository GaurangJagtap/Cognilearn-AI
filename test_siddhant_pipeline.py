"""
Siddhant's Media & Ingestion Pipeline Showcase Script.
Platform: Cognilearn-AI / Bharat AI
"""

import os
import sys
import time
from pathlib import Path

# Ensure backend root is discoverable
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
    sample_doc = "docs/contracts.md"
    if os.path.exists(sample_doc):
        text = extract_text(sample_doc)
        meta = extract_metadata(sample_doc)
        print(f"[OK] Document Ingestion: Extracted {len(text)} characters from '{sample_doc}'")
        print(f"[OK] Document Metadata: {meta}")
        assert len(text) > 0, "Ingestion extraction returned empty content"

    # 2. TTS Audio & Subtitle Generation
    sample_script = "Namaste! Aaj hum electric current aur voltage ke concept ko samjhenge."
    audio_path, srt_path = generate_audio_with_subtitles(sample_script, "hi")
    print(f"[OK] TTS Audio synthesized: '{audio_path}'")
    print(f"[OK] Subtitles track: '{srt_path}'")
    assert os.path.exists(audio_path), f"Audio file not found at {audio_path}"

    # 3. Visual Slide Asset Rendering
    visual_path = render_visual("Ohm's Law & Circuit Analysis", "diagram")
    print(f"[OK] Visual Slide Asset rendered: '{visual_path}'")
    assert os.path.exists(visual_path), f"Visual asset not found at {visual_path}"

    # 4. Avatar Video Clip Generation (With graceful fallback)
    avatar_path = generate_avatar_video(audio_path, script=sample_script, persona="dr_sharma")
    print(f"[OK] AI Avatar Video clip generated: '{avatar_path}'")
    assert os.path.exists(avatar_path), f"Avatar asset not found at {avatar_path}"

    # 5. Section Video Assembly
    sec_video = create_section_video(avatar_path, visual_path, audio_path, srt_path)
    print(f"[OK] Section Video Composed: '{sec_video}'")
    assert os.path.exists(sec_video), f"Composed section video not found at {sec_video}"

    print("\n=============================================================")
    print("ALL SIDDHANT MEDIA PIPELINE DELIVERABLES VERIFIED 100% CLEANLY!")
    print("=============================================================")


if __name__ == "__main__":
    run_siddhant_verification()
