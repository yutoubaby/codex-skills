#!/usr/bin/env python3
"""Render a narrated PDF/PPT/PPTX video using Edge TTS."""

from __future__ import annotations

import argparse
import asyncio
import json
import subprocess
import sys
from pathlib import Path

import edge_tts
from PIL import Image, ImageDraw, ImageFont

DEFAULT_VOICE = "zh-CN-XiaoxiaoNeural"


def run(*command: str) -> None:
    try:
        subprocess.run(command, check=True, capture_output=True)
    except FileNotFoundError as exc:
        raise RuntimeError(f"Missing required command: {command[0]}") from exc
    except subprocess.CalledProcessError as exc:
        detail = exc.stderr.decode("utf-8", "replace").strip()[-800:]
        raise RuntimeError(f"Command failed: {' '.join(command[:2])}: {detail}") from exc


def duration_seconds(audio: Path) -> float:
    result = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nw=1:nk=1", str(audio)], check=True, capture_output=True, text=True)
    return float(result.stdout.strip())


def timestamp(seconds: float) -> str:
    millis = max(0, round(seconds * 1000))
    hours, millis = divmod(millis, 3_600_000)
    minutes, millis = divmod(millis, 60_000)
    secs, millis = divmod(millis, 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"


def caption_chunks(text: str, limit: int = 28) -> list[str]:
    text = " ".join(text.split())
    if not text:
        return [""]
    chunks, current = [], ""
    for char in text:
        if len(current) >= limit and char in "，。！？；：,.!?;: ":
            chunks.append(current.strip())
            current = ""
        current += char
    if current.strip():
        chunks.append(current.strip())
    return chunks or [text]


def write_srt(scripts: list[str], durations: list[float], destination: Path) -> None:
    lines, number, offset = [], 1, 0.0
    for script, duration in zip(scripts, durations):
        chunks = caption_chunks(script)
        for index, chunk in enumerate(chunks):
            start = offset + duration * index / len(chunks)
            end = offset + duration * (index + 1) / len(chunks)
            lines.extend([str(number), f"{timestamp(start)} --> {timestamp(end)}", chunk, ""])
            number += 1
        offset += duration
    destination.write_text("\n".join(lines), encoding="utf-8")


def caption_events(scripts: list[str], durations: list[float]) -> list[tuple[str, float, float]]:
    events, offset = [], 0.0
    for script, duration in zip(scripts, durations):
        chunks = caption_chunks(script)
        for index, chunk in enumerate(chunks):
            events.append((chunk, offset + duration * index / len(chunks), offset + duration * (index + 1) / len(chunks)))
        offset += duration
    return events


def _caption_font(size: int) -> ImageFont.FreeTypeFont:
    candidates = ["/System/Library/Fonts/PingFang.ttc", "/System/Library/Fonts/Supplemental/Arial Unicode.ttf"]
    for candidate in candidates:
        if Path(candidate).is_file():
            return ImageFont.truetype(candidate, size)
    raise RuntimeError("No CJK-capable system font was found for caption rendering")


def parse_hex_color(value: str) -> tuple[int, int, int]:
    value = value.strip().lstrip("#")
    if len(value) != 6:
        raise RuntimeError("--subtitle-color must be a six-digit hex color, such as #FFFFFF")
    try:
        return tuple(int(value[index:index + 2], 16) for index in range(0, 6, 2))
    except ValueError as exc:
        raise RuntimeError("--subtitle-color must be a six-digit hex color, such as #FFFFFF") from exc


def burn_captions(video: Path, destination: Path, page_image: Path, scripts: list[str], durations: list[float], output: Path, style: str, text_color: tuple[int, int, int]) -> None:
    """Burn captions as raster overlays; works with FFmpeg builds without libass/drawtext."""
    with Image.open(page_image) as source:
        width, height = source.size
    overlay_dir = output / "caption-overlays"
    overlay_dir.mkdir(parents=True, exist_ok=True)
    font_size = max(36, width // (48 if style == "high_contrast" else 52))
    font = _caption_font(font_size)
    overlay_height = 210 if style == "high_contrast" else 180
    position_y = height - (250 if style == "high_contrast" else 220)
    overlays: list[Path] = []
    for number, (text, _, _) in enumerate(caption_events(scripts, durations), start=1):
        image = Image.new("RGBA", (width, overlay_height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        bounds = draw.textbbox((0, 0), text, font=font)
        text_width, text_height = bounds[2] - bounds[0], bounds[3] - bounds[1]
        box_left = max(0, (width - text_width) // 2 - 28)
        box_top = max(0, (overlay_height - text_height) // 2 - 18)
        box_right = min(width, (width + text_width) // 2 + 28)
        box_bottom = min(overlay_height, (overlay_height + text_height) // 2 + 18)
        if style == "high_contrast":
            draw.rounded_rectangle((box_left, box_top, box_right, box_bottom), radius=12, fill=(0, 0, 0, 210))
        elif style == "classic_bottom":
            draw.rounded_rectangle((box_left, box_top, box_right, box_bottom), radius=16, fill=(0, 0, 0, 150))
        text_position = ((width - text_width) // 2, (overlay_height - text_height) // 2 - bounds[1])
        if style == "minimal_bottom":
            draw.text(text_position, text, font=font, fill=text_color, stroke_width=3, stroke_fill=(0, 0, 0, 180))
        else:
            draw.text(text_position, text, font=font, fill=text_color)
        overlay = overlay_dir / f"caption_{number:03}.png"
        image.save(overlay)
        overlays.append(overlay)
    events = caption_events(scripts, durations)
    command = ["ffmpeg", "-y", "-i", str(video)]
    for overlay in overlays:
        command.extend(["-loop", "1", "-framerate", "25", "-i", str(overlay)])
    chain, previous = [], "[0:v]"
    for index, (_, start, end) in enumerate(events, start=1):
        target = f"[caption{index}]"
        chain.append(f"{previous}[{index}:v]overlay=0:{position_y}:enable='between(t,{start:.3f},{end:.3f})'{target}")
        previous = target
    command.extend(["-filter_complex", ";".join(chain), "-map", previous, "-map", "0:a?", "-c:v", "libx264", "-c:a", "copy", "-shortest", str(destination)])
    run(*command)


def edge_tts_synthesize(text: str, destination: Path, voice: str) -> None:
    """Synthesize one narration entry with Edge TTS (no API key required)."""

    async def _save() -> None:
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(str(destination))

    try:
        asyncio.run(_save())
    except Exception as exc:
        raise RuntimeError(f"Edge TTS synthesis failed for voice '{voice}': {exc}") from exc
    if not destination.is_file() or destination.stat().st_size == 0:
        raise RuntimeError("Edge TTS returned no audio; check the voice name and network access")


def source_pdf(source: Path, work: Path) -> Path:
    if source.suffix.lower() == ".pdf":
        return source
    if source.suffix.lower() not in {".ppt", ".pptx"}:
        raise RuntimeError("Input must be a PDF, PPT, or PPTX")
    run("soffice", "--headless", "--convert-to", "pdf", "--outdir", str(work), str(source))
    candidate = work / f"{source.stem}.pdf"
    if not candidate.exists():
        raise RuntimeError("LibreOffice did not produce a PDF")
    return candidate


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--scripts", required=True, type=Path, help="JSON array: one narration per page")
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--voice", default=DEFAULT_VOICE, help=f"Edge TTS voice name; defaults to {DEFAULT_VOICE}")
    parser.add_argument("--subtitle-style", choices=["classic_bottom", "minimal_bottom", "high_contrast"], default="classic_bottom")
    parser.add_argument("--subtitle-color", default="#FFFFFF", help="Six-digit hex color; defaults to #FFFFFF")
    args = parser.parse_args()
    if not args.input.is_file() or not args.scripts.is_file():
        raise RuntimeError("Both --input and --scripts must point to files")
    subtitle_color = parse_hex_color(args.subtitle_color)
    scripts = json.loads(args.scripts.read_text(encoding="utf-8"))
    if not isinstance(scripts, list) or not all(isinstance(item, str) and item.strip() for item in scripts):
        raise RuntimeError("--scripts must be a JSON array of non-empty strings")
    output = args.output_dir.resolve()
    pages, audio, segments = output / "pages", output / "audio", output / "segments"
    for directory in (pages, audio, segments):
        directory.mkdir(parents=True, exist_ok=True)
    pdf = source_pdf(args.input.resolve(), output)
    run("pdftoppm", "-png", "-r", "200", str(pdf), str(pages / "page"))
    images = sorted(pages.glob("page-*.png"))
    if len(images) != len(scripts):
        raise RuntimeError(f"Narration count ({len(scripts)}) does not match page count ({len(images)})")
    durations: list[float] = []
    for index, script in enumerate(scripts, start=1):
        mp3 = audio / f"audio_{index:03}.mp3"
        edge_tts_synthesize(script, mp3, args.voice)
        durations.append(duration_seconds(mp3))
        segment = segments / f"segment_{index:03}.mp4"
        run("ffmpeg", "-y", "-loop", "1", "-i", str(images[index - 1]), "-i", str(mp3), "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2", "-c:v", "libx264", "-tune", "stillimage", "-c:a", "aac", "-b:a", "192k", "-pix_fmt", "yuv420p", "-shortest", str(segment))
    srt = output / "captions.srt"
    write_srt(scripts, durations, srt)
    concat = output / "concat.txt"
    concat.write_text("\n".join(f"file '{path.resolve()}'" for path in sorted(segments.glob("*.mp4"))), encoding="utf-8")
    joined = output / "joined.mp4"
    run("ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat), "-c", "copy", str(joined))
    burn_captions(joined, output / "final.mp4", images[0], scripts, durations, output, args.subtitle_style, subtitle_color)
    print(output / "final.mp4")


if __name__ == "__main__":
    try:
        main()
    except (RuntimeError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
