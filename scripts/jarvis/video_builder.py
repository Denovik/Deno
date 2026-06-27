import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy import (
    VideoFileClip, AudioFileClip, VideoClip,
    concatenate_videoclips
)
from config import VIDEO_WIDTH, VIDEO_HEIGHT, VIDEO_FPS

FONT_PATH = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
FONT_SIZE_MAX = 90
TEXT_COLOR = (255, 0, 255)       # Magenta
STROKE_COLOR = (0, 0, 0)
STROKE_WIDTH = 5
WORDS_PER_CLIP = 1
TEXT_Y_RATIO = 0.78
MAX_TEXT_WIDTH = VIDEO_WIDTH - 60

# Cache pre-rendered text images für Performance
_text_cache: dict = {}


def _render_text_image(text: str) -> Image.Image:
    """Rendert Text auf transparentem RGBA-Bild, gibt PIL Image zurück."""
    text = text.replace("\n", " ").replace("\r", " ").strip()
    if not text:
        return Image.new("RGBA", (1, 1), (0, 0, 0, 0))
    if text in _text_cache:
        return _text_cache[text]

    font_size = FONT_SIZE_MAX
    font = None
    bbox = None
    while font_size >= 32:
        font = ImageFont.truetype(FONT_PATH, font_size)
        dummy = Image.new("RGBA", (1, 1))
        draw = ImageDraw.Draw(dummy)
        bbox = draw.textbbox((0, 0), text, font=font, stroke_width=STROKE_WIDTH)
        text_w = bbox[2] - bbox[0]
        if text_w <= MAX_TEXT_WIDTH:
            break
        font_size -= 4

    text_h = bbox[3] - bbox[1] + STROKE_WIDTH * 2 + 16
    canvas_w = bbox[2] - bbox[0] + STROKE_WIDTH * 2 + 16

    img = Image.new("RGBA", (canvas_w, text_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.text(
        (STROKE_WIDTH + 8 - bbox[0], STROKE_WIDTH + 8 - bbox[1]),
        text,
        font=font,
        fill=TEXT_COLOR,
        stroke_width=STROKE_WIDTH,
        stroke_fill=STROKE_COLOR,
    )
    _text_cache[text] = img
    return img


def _get_active_text(t: float, word_timings: list, script_text: str, duration: float):
    """Gibt das Wort zurück, das zum Zeitpunkt t gesprochen wird."""
    if word_timings and len(word_timings) > 1:
        words = word_timings
        for i in range(0, len(words), WORDS_PER_CLIP):
            group = words[i:i + WORDS_PER_CLIP]
            t_start = group[0]["start"]
            next_i = i + WORDS_PER_CLIP
            t_end = words[next_i]["start"] if next_i < len(words) else group[-1]["end"]
            if t_start <= t < t_end:
                return " ".join(w["word"] for w in group)
        return None
    else:
        # Fallback: gleichmäßig verteilt
        words = script_text.split()
        groups = [words[i:i + WORDS_PER_CLIP] for i in range(0, len(words), WORDS_PER_CLIP)]
        if not groups:
            return None
        chunk_dur = duration / len(groups)
        idx = int(t / chunk_dur)
        if idx < len(groups):
            return " ".join(groups[idx])
        return None


def _make_subtitle_frame(frame: np.ndarray, t: float, word_timings: list,
                          script_text: str, duration: float) -> np.ndarray:
    """Blendet das aktive Wort direkt in einen RGB-Frame ein."""
    text = _get_active_text(t, word_timings, script_text, duration)
    if not text:
        return frame

    text_img = _render_text_image(text)
    x = (VIDEO_WIDTH - text_img.width) // 2
    y = int(VIDEO_HEIGHT * TEXT_Y_RATIO)

    base = Image.fromarray(frame, "RGB")
    # RGBA-Text mit Alpha-Maske auf RGB-Frame kleben
    base.paste(text_img, (x, y), text_img)
    return np.array(base)


def build_video(audio_path: str, stock_video_path: str, script_text: str,
                output_path: str, word_timings: list = None) -> str:
    """Baut fertiges 9:16 Video aus Audio + Hintergrund + Untertitel."""
    print("[video_builder] Starte Video-Produktion...")

    _text_cache.clear()

    audio = AudioFileClip(audio_path)
    duration = audio.duration

    # Stock-Video laden und anpassen
    stock = VideoFileClip(stock_video_path)
    if stock.duration < duration:
        loops = int(duration / stock.duration) + 1
        stock = concatenate_videoclips([stock] * loops)
    stock = stock.subclipped(0, duration)

    # Auf 9:16 zuschneiden
    stock_ratio = stock.w / stock.h
    target_ratio = VIDEO_WIDTH / VIDEO_HEIGHT
    if stock_ratio > target_ratio:
        stock = stock.resized(height=VIDEO_HEIGHT)
        x_center = (stock.w - VIDEO_WIDTH) // 2
        stock = stock.cropped(x1=x_center, y1=0, x2=x_center + VIDEO_WIDTH, y2=VIDEO_HEIGHT)
    else:
        stock = stock.resized(width=VIDEO_WIDTH)
        if stock.h > VIDEO_HEIGHT:
            y_center = (stock.h - VIDEO_HEIGHT) // 2
            stock = stock.cropped(x1=0, y1=y_center, x2=VIDEO_WIDTH, y2=y_center + VIDEO_HEIGHT)

    wt = word_timings or []

    def make_frame(t):
        # Hintergrund-Frame holen (numpy array, shape: H x W x 3)
        frame = stock.get_frame(t).copy().astype(np.float32)

        # Dunkles Overlay: einfach mit numpy multiplizieren
        frame *= 0.65

        # Aktives Wort einbrennen
        text = _get_active_text(t, wt, script_text, duration)
        if text:
            text_arr = np.array(_render_text_image(text))  # H x W x 4 (RGBA)
            alpha = text_arr[:, :, 3:4].astype(np.float32) / 255.0
            rgb = text_arr[:, :, :3].astype(np.float32)
            th, tw = text_arr.shape[:2]
            x = (VIDEO_WIDTH - tw) // 2
            y = int(VIDEO_HEIGHT * TEXT_Y_RATIO)
            # Alpha-Composite nur auf den relevanten Ausschnitt
            region = frame[y:y + th, x:x + tw]
            frame[y:y + th, x:x + tw] = region * (1.0 - alpha) + rgb * alpha

        return frame.astype(np.uint8)

    final = VideoClip(make_frame, duration=duration).with_audio(audio)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    final.write_videofile(
        output_path,
        fps=VIDEO_FPS,
        codec="libx264",
        audio_codec="aac",
        temp_audiofile=output_path + ".temp.m4a",
        remove_temp=True,
        logger=None,
    )

    print(f"[video_builder] Video fertig: {os.path.basename(output_path)}")
    return output_path
