import os
import textwrap
try:
    # moviepy 2.x
    from moviepy import (
        VideoFileClip, AudioFileClip, CompositeVideoClip,
        ColorClip, TextClip, concatenate_videoclips
    )
except ImportError:
    # moviepy 1.x Fallback
    from moviepy.editor import (
        VideoFileClip, AudioFileClip, CompositeVideoClip,
        ColorClip, TextClip, concatenate_videoclips
    )
from config import VIDEO_WIDTH, VIDEO_HEIGHT, VIDEO_FPS


def build_video(audio_path: str, stock_video_path: str, script_text: str, output_path: str) -> str:
    """Baut fertiges 9:16 Video aus Audio + Stock + Untertitel. Gibt Output-Pfad zurück."""
    print("[video_builder] Starte Video-Produktion...")

    # Audio laden
    audio = AudioFileClip(audio_path)
    duration = audio.duration

    # Stock-Video laden und auf Audio-Länge anpassen
    stock = VideoFileClip(stock_video_path)
    if stock.duration < duration:
        # Video loopen wenn zu kurz
        loops = int(duration / stock.duration) + 1
        stock = concatenate_videoclips([stock] * loops)
    stock = stock.subclip(0, duration)

    # Auf 9:16 Hochformat zuschneiden (1080x1920)
    stock_ratio = stock.w / stock.h
    target_ratio = VIDEO_WIDTH / VIDEO_HEIGHT

    if stock_ratio > target_ratio:
        # Video zu breit → Breite anpassen, Höhe skalieren
        new_height = VIDEO_HEIGHT
        new_width = int(stock.w * (VIDEO_HEIGHT / stock.h))
        stock = stock.resize(height=new_height)
        x_center = (new_width - VIDEO_WIDTH) // 2
        stock = stock.crop(x1=x_center, y1=0, x2=x_center + VIDEO_WIDTH, y2=VIDEO_HEIGHT)
    else:
        # Video zu hoch → Höhe anpassen, Breite skalieren
        new_width = VIDEO_WIDTH
        stock = stock.resize(width=new_width)
        if stock.h > VIDEO_HEIGHT:
            y_center = (stock.h - VIDEO_HEIGHT) // 2
            stock = stock.crop(x1=0, y1=y_center, x2=VIDEO_WIDTH, y2=y_center + VIDEO_HEIGHT)

    # Leichte Abdunklung für bessere Lesbarkeit
    dark_overlay = ColorClip(size=(VIDEO_WIDTH, VIDEO_HEIGHT), color=[0, 0, 0], duration=duration)
    dark_overlay = dark_overlay.set_opacity(0.4)

    # Audio setzen
    stock = stock.set_audio(audio)

    # Untertitel erstellen — Text in Zeilen aufteilen
    lines = textwrap.wrap(script_text, width=30)
    words_per_chunk = 6
    chunks = [" ".join(lines[i:i+words_per_chunk]) for i in range(0, len(lines), words_per_chunk)]
    if not chunks:
        chunks = [script_text[:100]]

    text_clips = []
    chunk_duration = duration / len(chunks)
    for i, chunk in enumerate(chunks):
        txt = TextClip(
            chunk,
            fontsize=60,
            color="white",
            font="Arial-Bold",
            stroke_color="black",
            stroke_width=2,
            method="caption",
            size=(VIDEO_WIDTH - 80, None),
            align="center",
        )
        txt = txt.set_position(("center", VIDEO_HEIGHT - 400))
        txt = txt.set_start(i * chunk_duration).set_duration(chunk_duration)
        text_clips.append(txt)

    # Video zusammenbauen
    final = CompositeVideoClip([stock, dark_overlay] + text_clips)
    final = final.set_duration(duration)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    final.write_videofile(
        output_path,
        fps=VIDEO_FPS,
        codec="libx264",
        audio_codec="aac",
        temp_audiofile=output_path + ".temp.m4a",
        remove_temp=True,
        verbose=False,
        logger=None,
    )

    print(f"[video_builder] Video fertig: {os.path.basename(output_path)}")
    return output_path
