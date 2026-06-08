# MiMo V2.5 Voice Design Troubleshooting & Tips

## `voicedesign` Model Parameter Constraints

The `mimo-v2.5-tts-voicedesign` model is used to create new voices based on text descriptions. It has specific API constraints compared to the standard TTS model.

### The `audio.voice` Pitfall
**Problem**: Passing the `voice` parameter (e.g., `"voice": "茉莉"`) to the `voicedesign` model results in an API error:
`Error code: 400 - {'error': {'code': '400', 'message': 'Param Incorrect', 'param': 'audio.voice is not supported for voice design model', 'type': ''}}`

**Fix**: The `mimo_tts.py` adapter script was patched to conditionally omit the `voice` parameter when the model is set to `voicedesign`.

### Tone Refinement: "Teen Girl" vs "Child"
When aiming for a "cute girl" or "anime girl" voice:
- **Child-like (Avoid if not requested)**: Using terms like "邻家妹妹" (neighbor's little sister) or "撒娇" (coquettish/spoiled) can sometimes trigger a very young, child-like tone.
- **Teen Girl (Preferred)**: Specify the age (e.g., "17-18 years old") and use descriptions like "青春少女" (youthful girl), "清亮甜美但不幼稚" (clear and sweet but not childish), and "元气学妹" (energetic junior/underclassman) to achieve a more mature but still youthful anime-style voice.

## Code Extraction Pattern
To extract a newly designed voice's audio via `canvas` or `evaluate` (if generated within a browser/canvas context):
1. Wait for the "Generated image" or "Edit" signal.
2. Find the `img` element with a source containing `backend-api`.
3. Use a `canvas` to draw the image and export it as `data:image/png`.

## Script Error Handling: `TypeError: unhashable type: 'slice'`

**Problem**: During an API failure (non-200), the `mimo_tts.py` script may crash with a `TypeError` if it attempts to slice the response body (`body[:500]`) when `body` has been parsed into a dictionary (unsliceable).

**Fix**: Always cast the response body to a string before slicing in error logs.
- **Good**: `print(f"ERROR: Response body: {str(body)[:500]}", file=sys.stderr)`
- **Bad**: `print(f"ERROR: Response format: {body[:500]}", file=sys.stderr)`

