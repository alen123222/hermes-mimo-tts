# Terminal Fallback Pattern: Direct MiMo Script Invocation

When `text_to_speech` tool is unavailable (e.g. mid-session before `/reset`), use
`terminal()` to invoke the MiMo script directly instead.

## Standard Invocation

```bash
/usr/local/bin/mimo_tts.py \
  --text "(温柔 撒娇)主人~ [轻笑] 语音脚本内容" \
  --output-path /tmp/voice-<timestamp>.wav \
  --voice 茉莉 \
  --model mimo-v2.5-tts \
  --style "年轻御姐高冷，干脆利落，语速有起伏，语句间带微弱气息音"
```

## Parameters Reference

| Parameter | Description | Default |
|-----------|-------------|---------|
| `--text` | Assistant-message text with audio tags | Required (or --input-path) |
| `--input-path` | Read text from file | Alternative to --text |
| `--output-path` | Output WAV path | Required |
| `--voice` | Voice name | 茉莉 |
| `--model` | Model ID | mimo-v2.5-tts |
| `--style` | User-message style/director instruction | "" |
| `--format` | Output format: wav / mp3 / pcm16 | wav |

## Output Format: MP3 Support

Use `--format mp3` to auto-convert to MP3 via ffmpeg after generation.
The output path stays `*.wav` as argument but the actual file becomes `*.mp3`:

```bash
/usr/local/bin/mimo_tts.py \
  --text "(温柔)主人您好~" \
  --output-path /tmp/voice-<timestamp>.wav \
  --voice 茉莉 \
  --model mimo-v2.5-tts \
  --format mp3 \
  --style "温柔御姐"
# → Actual file: /tmp/voice-<timestamp>.mp3 (~1/10 size of WAV)
```

## After Success

The script prints: `OK: N bytes written to <path>`

Attach the output path to your final reply as:
```
MEDIA:/tmp/voice-xxx.wav   # ← or .mp3 if --format mp3
```

## Provider Verification

When user asks "is this MiMo or Edge?", confirm from:

| Signal | MiMo | Edge |
|--------|------|------|
| Script path | `/usr/local/bin/mimo_tts.py` | N/A |
| API endpoint | `api.xiaomimimo.com` | (built-in) |
| Model name | `mimo-v2.5-tts` | N/A |
| Auth key | `XIAOMI_API_KEY` | None needed |
