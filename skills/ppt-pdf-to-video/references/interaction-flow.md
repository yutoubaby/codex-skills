# Interaction flow

## 1. Narration review — required

Show the draft in a page-by-page table: page number, narration, and estimated duration. Ask: “请确认口播稿，或告诉我需要调整的页码与方向。确认后我才会生成语音。” Stop here until the user approves.

## 2. Voice choice — required

Offer a small set of voice choices that users can understand without knowing Edge TTS:

- Describe each option by tone, apparent gender where relevant, and use case, such as **稳重专业男声（推荐）**、**活力讲解男声** or **知性温和女声**.
- Give each option a number and a one-line description. The user should be able to reply with a number or the plain-language name.
- Resolve the plain-language choice to an Edge TTS voice name yourself (see `references/edge-tts.md`). Show the resolved voice name for transparency, but do not ask the user to supply one.

Never pick a voice automatically; the user may explicitly accept a recommendation.

## 3. Subtitle treatment — optional

Ask: “字幕想用什么风格和颜色？不指定则使用底部白字、半透明深色圆角底。” If the user has no preference, use:

- Style: `classic_bottom`
- Text color: `#FFFFFF`

Other renderer styles are `minimal_bottom` (outlined text without a background box) and `high_contrast` (larger text with a darker box).

## 4. Render confirmation — required

Briefly restate the narration status, chosen voice model, and subtitle treatment. Render only after the user confirms this summary.
