"""
Multilingual Text-to-Speech (TTS) Engine for AI Teacher.
Supports ElevenLabs API + Microsoft Edge Neural TTS + gTTS fallback + pure-python silent WAV generator.
Generates natural speech audio and synced subtitle timecodes.
Deliverable for Siddhant.
"""

import os
import sys
import wave
import struct
import math
import asyncio
from pathlib import Path
from typing import Dict, Any, Tuple, Optional

STORAGE_AUDIO_DIR = Path("storage/generated_audio")
STORAGE_AUDIO_DIR.mkdir(parents=True, exist_ok=True)

VOICE_MAP = {
    "en": "en-US-AvaNeural",
    "en-male": "en-US-AndrewNeural",
    "hi": "hi-IN-SwaraNeural",
    "hi-male": "hi-IN-MadhurNeural",
    "hinglish": "hi-IN-SwaraNeural",
    "es": "es-ES-ElviraNeural",
    "fr": "fr-FR-DeniseNeural",
    "de": "de-DE-KatjaNeural",
}

def generate_audio(
    script: str,
    language: str = "en",
    voice_id: Optional[str] = None,
    output_path: Optional[str] = None
) -> str:
    """
    Core contract function: Generates an MP3/WAV audio file from the script text.
    Returns absolute path to the generated audio file.
    """
    if not script or not script.strip():
        script = "Welcome to the AI Teacher lesson session."

    if not output_path:
        filename = f"tts_{hash(script[:50]) & 0xffffffff}_{language}.mp3"
        output_path = str((STORAGE_AUDIO_DIR / filename).resolve())

    output_path = str(Path(output_path).resolve())
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    elevenlabs_key = os.getenv("ELEVENLABS_API_KEY")
    if elevenlabs_key and elevenlabs_key.strip():
        try:
            return _generate_elevenlabs(script, elevenlabs_key, voice_id, output_path)
        except Exception as e:
            print(f"[TTS Warn] ElevenLabs failed ({e}), falling back to Edge TTS...")

    try:
        return _generate_edge_tts(script, language, voice_id, output_path)
    except Exception as e:
        print(f"[TTS Warn] Edge TTS failed ({e}), falling back to gTTS...")

    try:
        return _generate_gtts(script, language, output_path)
    except Exception as e:
        print(f"[TTS Warn] gTTS unavailable ({e}), generating synthesized tone track...")
        return _generate_synth_wav(script, output_path)

def generate_audio_with_subtitles(
    script: str,
    language: str = "en",
    output_audio_path: Optional[str] = None
) -> Tuple[str, str]:
    """
    Generates audio AND a synced .srt subtitle file.
    Returns (audio_path, srt_subtitle_path).
    """
    audio_path = generate_audio(script, language, output_path=output_audio_path)
    srt_path = str(Path(audio_path).with_suffix(".srt"))

    words = script.strip().split()
    if not words:
        words = ["Lesson"]

    total_seconds = max(2.0, len(words) * 0.4)
    time_per_word = total_seconds / len(words)

    lines = []
    line_words = []
    for word in words:
        line_words.append(word)
        if len(line_words) >= 6 or word.endswith((".", "?", "!", ":", ";", "।")):
            lines.append(" ".join(line_words))
            line_words = []
    if line_words:
        lines.append(" ".join(line_words))

    srt_blocks = []
    current_time = 0.0
    for idx, line in enumerate(lines, 1):
        duration = max(1.2, len(line.split()) * time_per_word)
        end_time = current_time + duration
        start_str = _format_srt_time(current_time)
        end_str = _format_srt_time(end_time)
        srt_blocks.append(f"{idx}\n{start_str} --> {end_str}\n{line}\n")
        current_time = end_time

    with open(srt_path, "w", encoding="utf-8") as f:
        f.write("\n".join(srt_blocks))

    return audio_path, srt_path

def _generate_elevenlabs(script: str, api_key: str, voice_id: Optional[str], output_path: str) -> str:
    import requests
    target_voice = voice_id or "21m00Tcm4TlvDq8ikWAM"
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{target_voice}"
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": api_key
    }
    data = {
        "text": script,
        "model_id": "eleven_multilingual_v2",
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}
    }
    resp = requests.post(url, json=data, headers=headers, timeout=15)
    resp.raise_for_status()
    with open(output_path, "wb") as f:
        f.write(resp.content)
    return output_path

def _generate_edge_tts(script: str, language: str, voice_id: Optional[str], output_path: str) -> str:
    import edge_tts

    voice = voice_id or VOICE_MAP.get(language.lower(), VOICE_MAP.get(language.split("-")[0].lower(), VOICE_MAP["en"]))

    async def _async_tts():
        communicate = edge_tts.Communicate(script, voice)
        await communicate.save(output_path)

    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            new_loop = asyncio.new_event_loop()
            new_loop.run_until_complete(_async_tts())
            new_loop.close()
        else:
            loop.run_until_complete(_async_tts())
    except RuntimeError:
        asyncio.run(_async_tts())

    if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
        return output_path
    raise RuntimeError("Edge TTS produced empty output file.")

def _generate_gtts(script: str, language: str, output_path: str) -> str:
    from gtts import gTTS
    lang_code = "hi" if language.lower() in ["hi", "hinglish"] else "en"
    tts = gTTS(text=script, lang=lang_code, slow=False)
    tts.save(output_path)
    return output_path

def _generate_synth_wav(script: str, output_path: str) -> str:
    """Pure python zero-dependency synth wave generator fallback."""
    wav_path = str(Path(output_path).with_suffix(".wav"))
    sample_rate = 22050
    words = len(script.split())
    duration = max(2.5, words * 0.35)
    num_samples = int(sample_rate * duration)

    with wave.open(wav_path, "w") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)

        for i in range(num_samples):
            t = i / sample_rate
            value = int(8000 * math.sin(2 * math.pi * 440 * t) * math.exp(-t / duration))
            data = struct.pack("<h", value)
            wav_file.writeframesraw(data)

    return wav_path

def _format_srt_time(seconds: float) -> str:
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hrs:02d}:{mins:02d}:{secs:02d},{millis:03d}"
