# Edge TTS

The renderer synthesizes speech with the open-source `edge-tts` package (Microsoft Edge online voices). No API key, account, or local model is required; only network access.

- Default voice: `zh-CN-XiaoxiaoNeural`
- Pass any voice with `--voice <name>`, for example `zh-CN-YunxiNeural`.
- List all available voices with `edge-tts --list-voices` (filter with `| grep zh-CN` for Chinese voices).

## Common Chinese voices

| Voice name | Tone |
|---|---|
| `zh-CN-XiaoxiaoNeural` | 知性温和女声（默认） |
| `zh-CN-XiaoyiNeural` | 亲和自然女声 |
| `zh-CN-YunxiNeural` | 活力讲解男声 |
| `zh-CN-YunjianNeural` | 浑厚有力男声 |
| `zh-CN-YunyangNeural` | 稳重专业男声（新闻播报） |

Other locales follow the same `<locale>-<Name>Neural` pattern, such as `en-US-AndrewMultilingualNeural` or `ja-JP-NanamiNeural`.
