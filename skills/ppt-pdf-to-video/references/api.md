# Legacy API note

The previous FastAPI demo is not bundled with this skill, so its `/api/*` routes are not a supported contract. Use `scripts/render_video.py` for the portable workflow.

For a web integration, implement an API around that script. The agent generates narration before rendering; Edge TTS only synthesizes supplied text.
