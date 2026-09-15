# Rendering pipeline

1. Convert PPT/PPTX to PDF with LibreOffice.
2. Render the PDF to PNG pages with Poppler at 200 DPI.
3. Have the agent create one narration entry per page.
4. Generate an MP3 for each entry through Edge TTS.
5. Measure each MP3 with FFmpeg, create an SRT with proportional caption timing, and compose a still-image video segment.
6. Concatenate segments and render the captions as image overlays into `final.mp4`. This works even when FFmpeg lacks the optional `subtitles` or `drawtext` filters.

## Troubleshooting

- Missing `soffice`: provide PDF input or install LibreOffice.
- Missing Poppler: install the package that supplies `pdftoppm`.
- Edge TTS failure: check network access and verify the voice name with `edge-tts --list-voices`; do not retry blindly.
- Font fallback in captions: the renderer needs a CJK-capable system font; on macOS it uses PingFang when available.
- H.264 requires even page dimensions; the renderer automatically rounds image dimensions down to even values.
