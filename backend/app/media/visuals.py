"""
Subject-Aware Visual Asset Renderer for AI Teacher.
Generates static 1080p HD glassmorphic slides AND animated MP4 visual motion graphics.
Deliverable for Siddhant.
"""

import os
import math
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageDraw, ImageFont

STORAGE_VISUALS_DIR = Path("storage/generated_visuals")
STORAGE_VISUALS_DIR.mkdir(parents=True, exist_ok=True)

BG_DARK = (11, 15, 25)
CARD_BG = (22, 28, 45, 230)
ACCENT_CYAN = (56, 189, 248)
ACCENT_PURPLE = (168, 85, 247)
ACCENT_EMERALD = (52, 211, 153)
TEXT_WHITE = (248, 250, 252)
TEXT_MUTED = (148, 163, 184)

CANVAS_WIDTH = 1920
CANVAS_HEIGHT = 1080
FPS = 25

def render_visual(
    concept: str,
    visual_type: str,
    details: Optional[Dict[str, Any]] = None,
    output_path: Optional[str] = None
) -> str:
    """
    Core contract function: Renders a static subject-aware visual asset image (.png).
    Returns absolute path to generated image.
    """
    details = details or {}
    visual_type = (visual_type or "slide").lower()

    if not output_path:
        filename = f"visual_{hash(concept[:40] + visual_type) & 0xffffffff}.png"
        output_path = str((STORAGE_VISUALS_DIR / filename).resolve())

    output_path = str(Path(output_path).resolve())
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    if "graph" in visual_type or "math" in visual_type:
        _render_graph_visual(concept, details, output_path)
    elif "code" in visual_type or "program" in visual_type:
        _render_code_visual(concept, details, output_path)
    elif "diagram" in visual_type or "biology" in visual_type or "circuit" in visual_type:
        _render_diagram_visual(concept, details, output_path)
    elif "timeline" in visual_type or "history" in visual_type:
        _render_timeline_visual(concept, details, output_path)
    else:
        _render_slide_visual(concept, details, output_path)

    return output_path

def render_animated_visual(
    concept: str,
    visual_type: str,
    duration: float = 5.0,
    details: Optional[Dict[str, Any]] = None,
    output_path: Optional[str] = None
) -> str:
    details = details or {}
    visual_type = (visual_type or "slide").lower()

    if not output_path:
        filename = f"motion_{hash(concept + visual_type) & 0xffffffff}.mp4"
        output_path = str((STORAGE_VISUALS_DIR / filename).resolve())

    output_path = str(Path(output_path).resolve())
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    total_frames = max(int(duration * FPS), FPS * 2)
    temp_frames_dir = STORAGE_VISUALS_DIR / f"motion_frames_{hash(concept) & 0xffffffff}"
    temp_frames_dir.mkdir(parents=True, exist_ok=True)

    for idx in range(total_frames):
        progress = idx / (total_frames - 1)
        if "graph" in visual_type:
            frame_img = _draw_animated_graph_frame(concept, details, progress)
        elif "code" in visual_type:
            frame_img = _draw_animated_code_frame(concept, details, progress)
        elif "diagram" in visual_type:
            frame_img = _draw_animated_diagram_frame(concept, details, progress)
        else:
            frame_img = _draw_animated_slide_frame(concept, details, progress)

        frame_p = temp_frames_dir / f"frame_{idx:05d}.png"
        frame_img.save(frame_p)

    pattern = str(temp_frames_dir / "frame_%05d.png")
    cmd = [
        "ffmpeg", "-y",
        "-framerate", str(FPS),
        "-i", pattern,
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "fast",
        output_path
    ]
    subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    for f in temp_frames_dir.glob("*.png"):
        try:
            f.unlink()
        except OSError:
            pass
    try:
        temp_frames_dir.rmdir()
    except OSError:
        pass

    if os.path.exists(output_path):
        return output_path
    return render_visual(concept, visual_type, details)

def _draw_animated_graph_frame(concept: str, details: Dict[str, Any], progress: float) -> Image.Image:
    fig, ax = plt.subplots(figsize=(16, 9), dpi=120)
    fig.patch.set_facecolor("#0B0F19")
    ax.set_facecolor("#161C2D")

    x_full = np.linspace(-10, 10, 500)
    cutoff = max(5, int(len(x_full) * progress))
    x = x_full[:cutoff]

    y1 = np.sin(x)
    y2 = np.cos(x)

    ax.plot(x, y1, color="#38BDF8", linewidth=4, label="Current I(t) = sin(t)")
    ax.plot(x, y2, color="#A855F7", linewidth=4, linestyle="--", label="Voltage V(t) = cos(t)")
    ax.fill_between(x, y1, y2, color="#38BDF8", alpha=0.15)

    ax.set_xlim(-10, 10)
    ax.set_ylim(-1.5, 1.5)
    ax.set_title(f"Dynamic Motion Graph: {concept.title()}", color="#F8FAFC", fontsize=20, pad=20, fontweight="bold")
    ax.set_xlabel("Time (t)", color="#94A3B8", fontsize=14)
    ax.set_ylabel("Amplitude", color="#94A3B8", fontsize=14)
    ax.tick_params(colors="#94A3B8", labelsize=12)
    ax.grid(True, color="#334155", linestyle=":", alpha=0.6)

    legend = ax.legend(facecolor="#0F172A", edgecolor="#38BDF8", fontsize=14)
    for text in legend.get_texts():
        text.set_color("#F8FAFC")

    plt.tight_layout()
    temp_p = str(STORAGE_VISUALS_DIR / f"temp_plt_{hash(progress) & 0xffffffff}.png")
    plt.savefig(temp_p, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close()

    img = Image.open(temp_p).convert("RGBA").resize((CANVAS_WIDTH, CANVAS_HEIGHT))
    try:
        os.remove(temp_p)
    except OSError:
        pass
    return img

def _draw_animated_code_frame(concept: str, details: Dict[str, Any], progress: float) -> Image.Image:
    img = _create_base_canvas()
    draw = ImageDraw.Draw(img)

    code_snippet = details.get("code") or (
        "def calculate_current(v: float, r: float) -> float:\n"
        "    if r <= 0:\n"
        "        raise ValueError('Resistance must be > 0')\n"
        "    return v / r\n\n"
        "current = calculate_current(12.0, 4.0)\n"
        "print(f'Current = {current} A')"
    )

    margin_x, margin_y = 180, 120
    card_w = CANVAS_WIDTH - 2 * margin_x
    card_h = CANVAS_HEIGHT - 2 * margin_y

    draw.rounded_rectangle([margin_x, margin_y, margin_x + card_w, margin_y + card_h], radius=18, fill=(15, 23, 42, 245), outline=(56, 189, 248, 140), width=2)
    draw.rounded_rectangle([margin_x, margin_y, margin_x + card_w, margin_y + 55], radius=18, fill=(30, 41, 59, 255))
    draw.ellipse([margin_x + 25, margin_y + 18, margin_x + 43, margin_y + 36], fill=(239, 68, 68))
    draw.ellipse([margin_x + 55, margin_y + 18, margin_x + 73, margin_y + 36], fill=(245, 158, 11))
    draw.ellipse([margin_x + 85, margin_y + 18, margin_x + 103, margin_y + 36], fill=(34, 197, 94))
    draw.text((margin_x + 140, margin_y + 16), f"solution.py — {concept.title()}", font=_get_font(20, bold=True), fill=TEXT_MUTED)

    lines = code_snippet.split("\n")
    active_idx = min(len(lines) - 1, int(progress * len(lines)))
    font_code = _get_font(24, monospace=True)

    y_pos = margin_y + 80
    for idx, line in enumerate(lines):
        if idx == active_idx:
            draw.rounded_rectangle([margin_x + 15, y_pos - 4, margin_x + card_w - 15, y_pos + 32], radius=6, fill=(56, 189, 248, 40), outline=ACCENT_CYAN, width=1)

        draw.text((margin_x + 30, y_pos), f"{idx+1:2d}", font=font_code, fill=(100, 116, 139))
        color = ACCENT_CYAN if idx == active_idx else TEXT_WHITE
        draw.text((margin_x + 90, y_pos), line, font=font_code, fill=color)
        y_pos += 38

    return img

def _draw_animated_diagram_frame(concept: str, details: Dict[str, Any], progress: float) -> Image.Image:
    img = _create_base_canvas()
    draw = ImageDraw.Draw(img)

    draw.text((120, 80), f"Diagram Flow: {concept.title()}", font=_get_font(44, bold=True), fill=TEXT_WHITE)

    nodes = details.get("nodes") or [
        {"title": "Voltage Source", "desc": "Pushes charges", "color": ACCENT_CYAN},
        {"title": "Conductor Wire", "desc": "Carries charge flow", "color": ACCENT_PURPLE},
        {"title": "Resistor Load", "desc": "Limits current", "color": ACCENT_EMERALD}
    ]

    active_node = min(len(nodes) - 1, int(progress * len(nodes)))

    start_x = 180
    y_center = 520
    box_w, box_h = 420, 220
    gap = 180

    for i, node in enumerate(nodes):
        x = start_x + i * (box_w + gap)
        rect = [x, y_center - box_h//2, x + box_w, y_center + box_h//2]

        is_active = (i == active_node)
        color = node["color"] if not is_active else (255, 255, 255)
        border_w = 5 if is_active else 2

        draw.rounded_rectangle(rect, radius=18, fill=(22, 28, 45, 235), outline=color, width=border_w)
        draw.rounded_rectangle([rect[0], rect[1], rect[2], rect[1] + 50], radius=18, fill=node["color"] + (80 if is_active else 40,))
        draw.text((x + 25, rect[1] + 12), node["title"], font=_get_font(24, bold=True), fill=TEXT_WHITE)
        draw.text((x + 25, rect[1] + 80), node["desc"], font=_get_font(18), fill=TEXT_MUTED)

        if i < len(nodes) - 1:
            arrow_start = (x + box_w, y_center)
            arrow_end = (x + box_w + gap, y_center)
            draw.line([arrow_start, arrow_end], fill=ACCENT_CYAN, width=5)
            draw.polygon([arrow_end, (arrow_end[0] - 20, arrow_end[1] - 12), (arrow_end[0] - 20, arrow_end[1] + 12)], fill=ACCENT_CYAN)

    return img

def _draw_animated_slide_frame(concept: str, details: Dict[str, Any], progress: float) -> Image.Image:
    return render_visual_image_canvas(concept, details)

def _create_base_canvas() -> Image.Image:
    img = Image.new("RGBA", (CANVAS_WIDTH, CANVAS_HEIGHT), BG_DARK + (255,))
    draw = ImageDraw.Draw(img)
    for x in range(0, CANVAS_WIDTH, 80):
        draw.line([(x, 0), (x, CANVAS_HEIGHT)], fill=(30, 41, 59, 60), width=1)
    for y in range(0, CANVAS_HEIGHT, 80):
        draw.line([(0, y), (CANVAS_WIDTH, y)], fill=(30, 41, 59, 60), width=1)
    draw.rectangle([(0, 0), (CANVAS_WIDTH, 8)], fill=ACCENT_CYAN + (255,))
    return img

def _render_slide_visual(concept: str, details: Dict[str, Any], output_path: str):
    img = render_visual_image_canvas(concept, details)
    img.save(output_path)

def render_visual_image_canvas(concept: str, details: Dict[str, Any]) -> Image.Image:
    img = _create_base_canvas()
    draw = ImageDraw.Draw(img)

    font_title = _get_font(52, bold=True)
    font_sub = _get_font(32)
    font_body = _get_font(26)
    font_badge = _get_font(20, bold=True)

    card_margin = 120
    card_rect = [card_margin, 140, CANVAS_WIDTH - card_margin, CANVAS_HEIGHT - 120]
    draw.rounded_rectangle(card_rect, radius=24, fill=(22, 28, 45, 230), outline=(56, 189, 248, 120), width=2)

    badge_rect = [card_margin + 60, 180, card_margin + 260, 220]
    draw.rounded_rectangle(badge_rect, radius=12, fill=(56, 189, 248, 40), outline=ACCENT_CYAN + (200,), width=1)
    draw.text((card_margin + 80, 190), "KEY CONCEPT", font=font_badge, fill=ACCENT_CYAN)

    title_text = details.get("title", concept.title())
    draw.text((card_margin + 60, 245), title_text, font=font_title, fill=TEXT_WHITE)
    draw.line([(card_margin + 60, 315), (card_margin + 400, 315)], fill=ACCENT_PURPLE, width=4)

    formula = details.get("formula") or details.get("highlight", "V = I x R  (Ohm's Law)")
    box_rect = [card_margin + 60, 350, CANVAS_WIDTH - card_margin - 60, 440]
    draw.rounded_rectangle(box_rect, radius=16, fill=(15, 23, 42, 240), outline=ACCENT_EMERALD + (180,), width=2)
    draw.text((card_margin + 90, 375), f"Formula / Core Principle:  {formula}", font=font_sub, fill=ACCENT_EMERALD)

    explanation = details.get("explanation", "• Voltage (V) is directly proportional to Current (I).\n• Resistance (R) opposes current flow.")
    lines = [line.strip() for line in explanation.split("\n") if line.strip()]

    y_pos = 480
    for line in lines[:5]:
        if not line.startswith("•") and not line.startswith("-"):
            line = f"• {line}"
        draw.text((card_margin + 70, y_pos), line, font=font_body, fill=TEXT_MUTED)
        y_pos += 55

    draw.text((card_margin + 60, CANVAS_HEIGHT - 170), "AI Teacher Educator Platform • Interactive Session", font=_get_font(20), fill=(100, 116, 139))
    return img

def _render_graph_visual(concept: str, details: Dict[str, Any], output_path: str):
    fig, ax = plt.subplots(figsize=(16, 9), dpi=120)
    fig.patch.set_facecolor("#0B0F19")
    ax.set_facecolor("#161C2D")
    x = np.linspace(-10, 10, 500)
    ax.plot(x, np.sin(x), color="#38BDF8", linewidth=3, label="Current I(t) = sin(t)")
    ax.plot(x, np.cos(x), color="#A855F7", linewidth=3, linestyle="--", label="Voltage V(t) = cos(t)")
    ax.fill_between(x, np.sin(x), np.cos(x), color="#38BDF8", alpha=0.15)
    ax.set_title(f"Mathematical Plot: {concept.title()}", color="#F8FAFC", fontsize=20, pad=20, fontweight="bold")
    ax.set_xlabel("Time (t)", color="#94A3B8", fontsize=14)
    ax.set_ylabel("Amplitude", color="#94A3B8", fontsize=14)
    ax.tick_params(colors="#94A3B8", labelsize=12)
    ax.grid(True, color="#334155", linestyle=":", alpha=0.6)
    legend = ax.legend(facecolor="#0F172A", edgecolor="#38BDF8", fontsize=14)
    for text in legend.get_texts():
        text.set_color("#F8FAFC")
    plt.tight_layout()
    plt.savefig(output_path, facecolor=fig.get_facecolor(), edgecolor="none")
    plt.close()

def _render_code_visual(concept: str, details: Dict[str, Any], output_path: str):
    img = _create_base_canvas()
    draw = ImageDraw.Draw(img)
    code_snippet = details.get("code") or "def calculate_current(v, r):\n    return v / r\n\nprint(calculate_current(12, 4))"
    margin_x, margin_y = 180, 120
    card_w = CANVAS_WIDTH - 2 * margin_x
    card_h = CANVAS_HEIGHT - 2 * margin_y
    draw.rounded_rectangle([margin_x, margin_y, margin_x + card_w, margin_y + card_h], radius=18, fill=(15, 23, 42, 245), outline=(56, 189, 248, 140), width=2)
    draw.rounded_rectangle([margin_x, margin_y, margin_x + card_w, margin_y + 55], radius=18, fill=(30, 41, 59, 255))
    draw.ellipse([margin_x + 25, margin_y + 18, margin_x + 43, margin_y + 36], fill=(239, 68, 68))
    draw.ellipse([margin_x + 55, margin_y + 18, margin_x + 73, margin_y + 36], fill=(245, 158, 11))
    draw.ellipse([margin_x + 85, margin_y + 18, margin_x + 103, margin_y + 36], fill=(34, 197, 94))
    draw.text((margin_x + 140, margin_y + 16), f"solution.py — {concept.title()}", font=_get_font(20, bold=True), fill=TEXT_MUTED)
    lines = code_snippet.split("\n")
    font_code = _get_font(24, monospace=True)
    y_pos = margin_y + 80
    for idx, line in enumerate(lines, 1):
        draw.text((margin_x + 30, y_pos), f"{idx:2d}", font=font_code, fill=(100, 116, 139))
        draw.text((margin_x + 90, y_pos), line, font=font_code, fill=TEXT_WHITE)
        y_pos += 38
    img.save(output_path)

def _render_diagram_visual(concept: str, details: Dict[str, Any], output_path: str):
    img = _create_base_canvas()
    draw = ImageDraw.Draw(img)
    draw.text((120, 80), f"Concept Diagram: {concept.title()}", font=_get_font(44, bold=True), fill=TEXT_WHITE)
    
    raw_nodes = details.get("nodes")
    if not raw_nodes:
        raw_nodes = [
            {"title": f"{concept.title()} Input", "desc": "Initial state or component", "color": ACCENT_CYAN},
            {"title": "Core Function / Mechanism", "desc": f"Processes {concept}", "color": ACCENT_PURPLE},
            {"title": "Output / Effect", "desc": "Resulting system behavior", "color": ACCENT_EMERALD}
        ]
        
    nodes = []
    colors = [ACCENT_CYAN, ACCENT_PURPLE, ACCENT_EMERALD]
    for idx, n in enumerate(raw_nodes[:4]):
        if isinstance(n, dict):
            title = n.get("title") or n.get("label") or f"Node {idx+1}"
            desc = n.get("desc") or n.get("description") or f"Step {idx+1}"
            color = n.get("color") or colors[idx % len(colors)]
            nodes.append({"title": title, "desc": desc, "color": color})
        else:
            nodes.append({"title": str(n), "desc": f"Component {idx+1}", "color": colors[idx % len(colors)]})

    start_x = 180
    y_center = 520
    box_w = 420 if len(nodes) <= 3 else 320
    box_h = 220
    gap = 120 if len(nodes) <= 3 else 60

    for i, node in enumerate(nodes):
        x = start_x + i * (box_w + gap)
        rect = [x, y_center - box_h//2, x + box_w, y_center + box_h//2]
        c = node["color"] if isinstance(node["color"], tuple) else ACCENT_CYAN
        draw.rounded_rectangle(rect, radius=18, fill=(22, 28, 45, 235), outline=c + (200,), width=3)
        draw.rounded_rectangle([rect[0], rect[1], rect[2], rect[1] + 50], radius=18, fill=c + (40,))
        draw.text((x + 20, rect[1] + 12), node["title"][:22], font=_get_font(22, bold=True), fill=TEXT_WHITE)
        draw.text((x + 20, rect[1] + 75), node["desc"][:40], font=_get_font(16), fill=TEXT_MUTED)
        if i < len(nodes) - 1:
            arrow_start = (x + box_w, y_center)
            arrow_end = (x + box_w + gap, y_center)
            draw.line([arrow_start, arrow_end], fill=ACCENT_CYAN, width=5)
            draw.polygon([arrow_end, (arrow_end[0] - 16, arrow_end[1] - 10), (arrow_end[0] - 16, arrow_end[1] + 10)], fill=ACCENT_CYAN)
    img.save(output_path)

def _render_timeline_visual(concept: str, details: Dict[str, Any], output_path: str):
    img = _create_base_canvas()
    draw = ImageDraw.Draw(img)
    draw.text((120, 80), f"Roadmap: {concept.title()}", font=_get_font(44, bold=True), fill=TEXT_WHITE)
    milestones = details.get("milestones") or [
        {"phase": "Phase 1", "title": "Fundamentals"},
        {"phase": "Phase 2", "title": "Ohm's Law"},
        {"phase": "Phase 3", "title": "Circuit Analysis"},
        {"phase": "Phase 4", "title": "Advanced Apps"}
    ]
    y_line = 540
    draw.line([(180, y_line), (CANVAS_WIDTH - 180, y_line)], fill=ACCENT_CYAN, width=6)
    step = (CANVAS_WIDTH - 360) / (len(milestones) - 1)
    for idx, ms in enumerate(milestones):
        x = 180 + idx * step
        draw.ellipse([x - 22, y_line - 22, x + 22, y_line + 22], fill=(15, 23, 42), outline=ACCENT_CYAN, width=4)
        draw.ellipse([x - 10, y_line - 10, x + 10, y_line + 10], fill=ACCENT_CYAN)
        card_y = y_line - 200 if idx % 2 == 0 else y_line + 60
        card_rect = [x - 140, card_y, x + 140, card_y + 130]
        draw.rounded_rectangle(card_rect, radius=14, fill=(22, 28, 45, 235), outline=ACCENT_PURPLE, width=2)
        draw.text((x - 120, card_y + 20), ms["phase"], font=_get_font(20, bold=True), fill=ACCENT_PURPLE)
        draw.text((x - 120, card_y + 60), ms["title"], font=_get_font(22, bold=True), fill=TEXT_WHITE)
    img.save(output_path)

def _get_font(size: int, bold: bool = False, monospace: bool = False) -> ImageFont.FreeTypeFont:
    font_names = []
    if monospace:
        font_names = ["consola.ttf", "cour.ttf", "lucon.ttf", "DejaVuSansMono.ttf"]
    elif bold:
        font_names = ["arialbd.ttf", "segoeuib.ttf", "calibrib.ttf", "DejaVuSans-Bold.ttf"]
    else:
        font_names = ["arial.ttf", "segoeui.ttf", "calibri.ttf", "DejaVuSans.ttf"]
    for name in font_names:
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()
