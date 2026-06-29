import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import glob
import random
from moviepy import (
    VideoFileClip, AudioFileClip, VideoClip,
    CompositeAudioClip, concatenate_videoclips, concatenate_audioclips
)
from config import VIDEO_WIDTH, VIDEO_HEIGHT, VIDEO_FPS, BASE_DIR

MUSIC_DIR = os.path.join(BASE_DIR, "music")
MUSIC_VOLUME = 0.12   # 12% Lautstärke — Hintergrund, übertönt die Stimme nicht

_FONT_CANDIDATES = [
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",   # macOS
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",  # Linux
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",          # Linux fallback
]
FONT_PATH = next((p for p in _FONT_CANDIDATES if os.path.exists(p)), _FONT_CANDIDATES[0])
FONT_SIZE_MAX = 90
TEXT_COLOR = (255, 0, 255)       # Magenta
STROKE_COLOR = (0, 0, 0)
STROKE_WIDTH = 5
WORDS_PER_CLIP = 1
TEXT_Y_RATIO = 0.50
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


def _add_background_music(voice_audio, duration):
    """Mischt eine zufällige Musik aus music/ leise unter die Stimme. Ohne Musik: unverändert."""
    music_files = (
        glob.glob(os.path.join(MUSIC_DIR, "*.mp3"))
        + glob.glob(os.path.join(MUSIC_DIR, "*.m4a"))
        + glob.glob(os.path.join(MUSIC_DIR, "*.wav"))
    )
    if not music_files:
        return voice_audio

    track_path = random.choice(music_files)
    music = AudioFileClip(track_path)

    # Musik auf Videolänge bringen (loopen falls zu kurz, sonst zuschneiden)
    if music.duration < duration:
        loops = int(duration / music.duration) + 1
        music = concatenate_audioclips([music] * loops)
    music = music.subclipped(0, duration).with_volume_scaled(MUSIC_VOLUME)

    print(f"[video_builder] Hintergrundmusik: {os.path.basename(track_path)} ({int(MUSIC_VOLUME*100)}%)")
    return CompositeAudioClip([voice_audio, music])


def _fit_to_916(clip):
    """Schneidet einen Clip auf exakt 9:16 (1080x1920) zu."""
    target_ratio = VIDEO_WIDTH / VIDEO_HEIGHT
    src_ratio = clip.w / clip.h
    if src_ratio > target_ratio:
        clip = clip.resized(height=VIDEO_HEIGHT)
        x_center = (clip.w - VIDEO_WIDTH) // 2
        clip = clip.cropped(x1=x_center, y1=0, x2=x_center + VIDEO_WIDTH, y2=VIDEO_HEIGHT)
    else:
        clip = clip.resized(width=VIDEO_WIDTH)
        if clip.h > VIDEO_HEIGHT:
            y_center = (clip.h - VIDEO_HEIGHT) // 2
            clip = clip.cropped(x1=0, y1=y_center, x2=VIDEO_WIDTH, y2=y_center + VIDEO_HEIGHT)
    return clip


def build_video(audio_path: str, stock_video_path, script_text: str,
                output_path: str, word_timings: list = None) -> str:
    """Baut fertiges 9:16 Video. stock_video_path kann ein Pfad oder eine Liste von Pfaden sein."""
    print("[video_builder] Starte Video-Produktion...")

    _text_cache.clear()

    audio = AudioFileClip(audio_path)
    duration = audio.duration

    # Hintergrundmusik leise dazumischen (falls vorhanden)
    audio = _add_background_music(audio, duration)

    # Mehrere Stock-Videos zu einem Hintergrund zusammensetzen
    paths = stock_video_path if isinstance(stock_video_path, list) else [stock_video_path]
    clip_duration = duration / len(paths)  # Jedes Video bekommt gleichviel Zeit

    segments = []
    for p in paths:
        c = VideoFileClip(p)
        c = _fit_to_916(c)
        # Clip auf seinen Zeitslot kürzen (loopen wenn zu kurz)
        if c.duration < clip_duration:
            loops = int(clip_duration / c.duration) + 1
            c = concatenate_videoclips([c] * loops)
        c = c.subclipped(0, clip_duration)
        segments.append(c)

    stock = concatenate_videoclips(segments) if len(segments) > 1 else segments[0]

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
    # Instagram-kompatible Einstellungen: H.264 Main Profile, yuv420p, AAC
    final.write_videofile(
        output_path,
        fps=VIDEO_FPS,
        codec="libx264",
        audio_codec="aac",
        audio_bitrate="192k",
        temp_audiofile=output_path + ".temp.m4a",
        remove_temp=True,
        logger=None,
        ffmpeg_params=[
            "-profile:v", "main",
            "-pix_fmt", "yuv420p",
            "-movflags", "+faststart",
            "-b:v", "5000k",
            "-maxrate", "5000k",
            "-bufsize", "10000k",
        ],
    )

    print(f"[video_builder] Video fertig: {os.path.basename(output_path)}")
    return output_path
