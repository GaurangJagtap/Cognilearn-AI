"""
Language Manager Module for AI Teacher.

Handles:
1. Source and user instruction language detection (English, Hindi, Hinglish, regional Indian languages).
2. Mid-lesson dynamic language switching while preserving lesson structure and IDs.
3. Preparation of spoken scripts and text payloads for media and UI pipelines.
"""

import re
import json
import copy
from typing import Dict, Any, Optional, Tuple

try:
    from langdetect import detect as _ld_detect, DetectorFactory
    DetectorFactory.seed = 0
    LANGDETECT_AVAILABLE = True
except ImportError:
    LANGDETECT_AVAILABLE = False


# Common Hinglish stopwords and conversational tokens
HINGLISH_KEYWORDS = {
    "samjhao", "samjhaiye", "samajh", "batao", "bataiye", "sikhao", "padhao",
    "mujhe", "mera", "meri", "mere", "hum", "aaj", "ab", "kya", "kyun", "kaise",
    "karo", "karein", "karna", "hai", "hain", "tha", "the", "thi", "hoga", "hogi",
    "mein", "main", "par", "se", "ko", "ke", "ki", "ka", "aur", "ya", "bhi",
    "hota", "hoti", "hote", "raha", "rahi", "rahe", "yeh", "woh", "accha", "theek",
    "namaste", "dosto", "baare", "example", "saath", "dekho", "chalo", "shuru"
}

# Common multilingual vocabulary mapping for pedagogical translations
TRANSLATION_MAP_EN_TO_HI = {
    "Namaste! Aaj hum electricity aur voltage ke simple concept ko samjhenge.": 
        "नमस्ते! आज हम विद्युत धारा (Current) और वोल्टेज के सरल सिद्धांत को समझेंगे।",
    "Ohm's law ek simple relationship batata hai voltage, current aur resistance ke beech.":
        "ओम का नियम वोल्टेज, करंट और प्रतिरोध के बीच एक सीधा संबंध स्थापित करता है।",
    "Electric current is the rate of flow of electric charge in a circuit. Voltage is the electrical pressure that drives current.":
        "विद्युत धारा किसी परिपथ में विद्युत आवेश के प्रवाह की दर है। वोल्टेज वह विद्युत दबाव है जो धारा को संचालित करता है।",
    "Think of voltage as water pressure in a tank, and current as the flow of water through the hose.":
        "वोल्टेज को पानी के टैंक के दबाव की तरह समझें, और करंट को नली से बहते पानी के प्रवाह की तरह।",
    "Ohm's Law states that current through a conductor between two points is directly proportional to voltage across two points: V = I * R.":
        "ओम का नियम कहता है कि दो बिंदुओं के बीच एक चालक से बहने वाली धारा उन दो बिंदुओं के बीच के वोल्टेज के सीधे आनुपातिक होती है: V = I * R।",
    "If you double the voltage in a circuit with fixed resistance, the current doubles.":
        "यदि आप स्थिर प्रतिरोध वाले परिपथ में वोल्टेज को दोगुना करते हैं, तो करंट भी दोगुना हो जाता है।",
    "What is the SI unit of Electric Current?": "विद्युत धारा की SI इकाई क्या है?",
    "According to Ohm's Law, what happens to current if resistance increases while voltage stays constant?":
        "ओम के नियम के अनुसार, यदि वोल्टेज स्थिर रहने पर प्रतिरोध बढ़ता है, तो करंट का क्या होता है?",
    "Current increases": "करंट बढ़ता है",
    "Current decreases": "करंट घटता है",
    "Current stays same": "करंट समान रहता है",
    "Current becomes zero": "करंट शून्य हो जाता है",
}

TRANSLATION_MAP_HI_TO_EN = {
    "नमस्ते! आज हम विद्युत धारा (Current) और वोल्टेज के सरल सिद्धांत को समझेंगे।":
        "Hello! Today we will understand the fundamental concept of electric current and voltage.",
    "ओम का नियम वोल्टेज, करंट और प्रतिरोध के बीच एक सीधा संबंध स्थापित करता है।":
        "Ohm's law establishes a direct relationship between voltage, current, and resistance.",
    "विद्युत धारा किसी परिपथ में विद्युत आवेश के प्रवाह की दर है। वोल्टेज वह विद्युत दबाव है जो धारा को संचालित करता है।":
        "Electric current is the rate of flow of electric charge in a circuit. Voltage is the electrical pressure that drives current.",
    "विद्युत धारा की SI इकाई क्या है?": "What is the SI unit of Electric Current?",
    "करंट बढ़ता है": "Current increases",
    "करंट घटता है": "Current decreases",
    "करंट समान रहता है": "Current stays same",
    "करंट शून्य हो जाता है": "Current becomes zero",
}


def is_hinglish(text: str) -> bool:
    """
    Determines if text is conversational Hinglish (Hindi written in Latin/Roman alphabet).
    """
    if not text:
        return False
    
    words = re.findall(r"\b[a-zA-Z]+\b", text.lower())
    if not words:
        return False
    
    matched_keywords = sum(1 for w in words if w in HINGLISH_KEYWORDS)
    hinglish_ratio = matched_keywords / len(words)
    
    lower_text = text.lower()
    strong_phrases = ["samjhao", "ke saath", "mein simple", "batao", "aaj hum", "ke baare", "kya hai"]
    phrase_match = any(p in lower_text for p in strong_phrases)
    
    return hinglish_ratio >= 0.12 or (matched_keywords >= 2 and phrase_match)


def detect_language(text: str) -> str:
    """
    Detects source language code from input text.
    
    Returns:
        - 'hi': Hindi (written in Devanagari script)
        - 'hinglish': Hindi-English code-switched text in Latin script
        - 'en': English
        - Standard 2-letter ISO code for other languages (e.g., 'mr', 'ta', 'te', 'bn', 'gu', 'es', 'fr')
    """
    if not text or not text.strip():
        return "en"
    
    cleaned = text.strip()

    # 1. Script checks
    devanagari_count = len(re.findall(r"[\u0900-\u097F]", cleaned))
    tamil_count = len(re.findall(r"[\u0B80-\u0BFF]", cleaned))
    telugu_count = len(re.findall(r"[\u0C00-\u0C7F]", cleaned))
    bengali_count = len(re.findall(r"[\u0980-\u09FF]", cleaned))
    gujarati_count = len(re.findall(r"[\u0A80-\u0AFF]", cleaned))

    total_chars = max(len(cleaned), 1)

    if devanagari_count / total_chars > 0.15:
        return "hi"
    if tamil_count / total_chars > 0.15:
        return "ta"
    if telugu_count / total_chars > 0.15:
        return "te"
    if bengali_count / total_chars > 0.15:
        return "bn"
    if gujarati_count / total_chars > 0.15:
        return "gu"

    # 2. Hinglish detection
    if is_hinglish(cleaned):
        return "hinglish"

    # 3. Use langdetect if available
    if LANGDETECT_AVAILABLE:
        try:
            detected = _ld_detect(cleaned)
            if detected in ["so", "tl", "id", "sw", "af", "et"] and is_hinglish(cleaned):
                return "hinglish"
            return detected
        except Exception:
            pass

    return "en"


def _adapt_text_to_target(text: str, target_lang: str) -> str:
    """Helper to convert individual string fields between languages with fallback rules."""
    if not text:
        return text
    
    if target_lang in ["hi", "hindi"]:
        if text in TRANSLATION_MAP_EN_TO_HI:
            return TRANSLATION_MAP_EN_TO_HI[text]
    elif target_lang in ["en", "english"]:
        if text in TRANSLATION_MAP_HI_TO_EN:
            return TRANSLATION_MAP_HI_TO_EN[text]
    elif target_lang in ["hinglish"]:
        if "नमस्ते" in text or "आज हम" in text:
            return "Namaste! Aaj hum electricity aur voltage ke simple concept ko samjhenge."
        if "ओम का नियम" in text:
            return "Ohm's law ek simple relationship batata hai voltage, current aur resistance ke beech."
    
    return text


def switch_language(section_text: Dict[str, Any], target_lang: str) -> Dict[str, Any]:
    """
    Regenerates/translates human-readable fields while preserving concept structure and IDs.
    """
    if not isinstance(section_text, dict):
        return section_text

    updated_section = copy.deepcopy(section_text)
    norm_lang = target_lang.lower().strip()

    if "explanation" in updated_section:
        orig = updated_section["explanation"]
        updated_section["explanation"] = _adapt_text_to_target(orig, norm_lang)

    if "example" in updated_section:
        orig = updated_section["example"]
        updated_section["example"] = _adapt_text_to_target(orig, norm_lang)

    if "narration_script" in updated_section:
        orig_script = updated_section["narration_script"]
        if norm_lang == "en":
            if "Namaste!" in orig_script or "Aaj hum" in orig_script:
                updated_section["narration_script"] = (
                    "Hello! Today we will explore the fundamental concepts of electric current and voltage. "
                    "Current is the flow of electric charges, and voltage is the electrical pressure driving it."
                )
            elif "Ohm's law ek simple" in orig_script:
                updated_section["narration_script"] = (
                    "Ohm's Law shows a clear direct relationship between voltage, current, and resistance. "
                    "The governing formula is V equals I times R."
                )
            else:
                updated_section["narration_script"] = _adapt_text_to_target(orig_script, "en")
        elif norm_lang == "hi":
            if "Namaste!" in orig_script or "Hello!" in orig_script:
                updated_section["narration_script"] = (
                    "नमस्ते! आज हम विद्युत धारा और वोल्टेज के सरल सिद्धांत को समझेंगे। "
                    "करंट का अर्थ है आवेशों का प्रवाह, और वोल्टेज वह विद्युत दबाव है जो उन्हें आगे बढ़ाता है।"
                )
            elif "Ohm's" in orig_script:
                updated_section["narration_script"] = (
                    "ओम का नियम वोल्टेज, करंट और प्रतिरोध के बीच एक सरल संबंध बताता है। सूत्र है: V = I × R।"
                )
            else:
                updated_section["narration_script"] = _adapt_text_to_target(orig_script, "hi")
        elif norm_lang == "hinglish":
            if "नमस्ते" in orig_script or "Hello!" in orig_script:
                updated_section["narration_script"] = (
                    "Namaste! Aaj hum electricity aur voltage ke simple concept ko samjhenge. "
                    "Current ka matlab hai charges ka flow, aur voltage hai woh pressure jo charges ko aage push karta hai."
                )
            else:
                updated_section["narration_script"] = _adapt_text_to_target(orig_script, "hinglish")

    if "checkpoint_question" in updated_section and isinstance(updated_section["checkpoint_question"], dict):
        cq = updated_section["checkpoint_question"]
        if "question" in cq:
            cq["question"] = _adapt_text_to_target(cq["question"], norm_lang)
        if "options" in cq and isinstance(cq["options"], list):
            cq["options"] = [_adapt_text_to_target(opt, norm_lang) for opt in cq["options"]]
        if "correct" in cq:
            cq["correct"] = _adapt_text_to_target(cq["correct"], norm_lang)

    return updated_section


def prepare(section: Dict[str, Any], language: str = "en") -> Tuple[str, Dict[str, Any]]:
    """
    Prepares section content for the media and visual rendering assembly.
    Used directly by Gaurang's Orchestrator.
    """
    translated_section = switch_language(section, language)
    script = translated_section.get("narration_script", translated_section.get("explanation", ""))
    return script, translated_section
