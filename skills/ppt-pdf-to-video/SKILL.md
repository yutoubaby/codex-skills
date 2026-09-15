---
name: ppt-pdf-to-video
description: Convert PDF, PPT, or PPTX into a narrated MP4 with burned-in captions. The executing agent writes and revises the narration; Edge TTS generates speech. Use for document-to-video workflows, per-page narration, previews, or final MP4 export.
---

# PPT/PDF to Video

Create a narrated video from a PDF, PPT, or PPTX. This skill is self-contained: it does not require a separate FastAPI project, an LLM API, or any API key.

## Requirements

- System tools: `ffmpeg`, `ffprobe`, `pdftoppm`; `soffice` is additionally required for PPT/PPTX input.
- Python 3.10+ with `edge-tts` and `Pillow` (`pip install -r requirements.txt`).
- Edge TTS needs network access but no key or account.

## Interaction workflow

Treat narration, voice, and rendering as separate user-visible stages. Do not synthesize speech or render an MP4 until the user has approved the narration.

1. Inspect the document pages and extracted text, then write natural narration yourself. Preserve factual claims and avoid reading dense slide text verbatim.
2. Present the draft page by page, with page numbers and estimated duration. Ask the user to edit, regenerate selected pages, or approve it. Save the approved narration as a JSON array in page order.
3. Before synthesis, present a short, language- and tone-appropriate list of plain-language voice choices (for example, **稳重专业男声**、**活力讲解男声**、**知性温和女声**). Give each a one-line description and a numbered option, and recommend one when appropriate. Resolve the selected Edge TTS voice name yourself; include its name for transparency, but never require the user to provide or understand a voice ID.
4. Ask whether the user wants a subtitle style or color. If they have no preference, use `classic_bottom` with white text (`#FFFFFF`): a readable rounded dark background at the bottom.
5. Summarize the approved narration, chosen voice, and subtitle settings. After user confirmation, run `scripts/render_video.py` and validate the final MP4. For revision requests, return to the earliest affected stage.

Read `references/interaction-flow.md` when you need the exact prompts or default settings.

## Render command

```bash
python scripts/render_video.py \
  --input deck.pptx \
  --scripts narration.json \
  --output-dir outputs/deck-video \
  --voice zh-CN-YunxiNeural \
  --subtitle-style classic_bottom \
  --subtitle-color "#FFFFFF"
```

`--voice` is optional and defaults to `zh-CN-XiaoxiaoNeural`. Use any Edge TTS voice name, such as `zh-CN-YunxiNeural` (male), `zh-CN-YunyangNeural` (male, news), or `zh-CN-XiaoyiNeural` (female); list all voices with `edge-tts --list-voices`.

Subtitle styles: `classic_bottom` (default), `minimal_bottom`, and `high_contrast`. Pass a six-digit hex color such as `#F6E58D` to change the caption text color.

## Output

- `pages/`: rendered page images
- `audio/`: Edge TTS MP3 files
- `captions.srt`: subtitles timed proportionally to generated audio
- `final.mp4`: final video with captions burned in

## Safety and quality

- No API keys or credentials are needed; keep it that way and never bundle secrets into this skill.
- Confirm the narration entry count equals the page count before rendering.
- Edge TTS calls need network access; failures include the underlying error message.
- For a production web product, use the standalone pipeline here as the reference. The legacy FastAPI demo is intentionally not a dependency of this skill.

## References

- `references/edge-tts.md` for the Edge TTS voices and usage.
- `references/pipeline.md` for the rendering layout and troubleshooting.
- `references/interaction-flow.md` for the approval gates, choice prompts, and defaults.
