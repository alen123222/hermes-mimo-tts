#!/usr/local/lib/hermes-agent/venv/bin/python3
"""
Xiaomi MiMo V2.5 TTS — 语音表演模型适配器。
官方 SDK: https://api.xiaomimimo.com/v1

使用：
  mimo_tts.py --text "朗读内容" --output-path out.wav --voice 茉莉 --style "温柔御姐音"
  mimo_tts.py --input-path text.txt --output-path out.wav --voice Chloe --model mimo-v2.5-tts
  mimo_tts.py --text "(唱歌)" --output-path song.wav --style "明亮摇滚" --format wav

消息结构：
  role: user       → 风格/导演指令（自然语言控制）
  role: assistant  → 实际朗读文本（支持音频标签）

完整参考：skill_view(name='mimo-tts-v2.5')
"""
import os, sys, argparse, base64
from openai import OpenAI


def _to_mp3(wav_path: str) -> str:
    """Convert WAV to MP3 via ffmpeg, replace the original file."""
    mp3_path = wav_path.replace(".wav", ".mp3")
    ret = os.system(f"ffmpeg -y -i {wav_path} -codec:a libmp3lame -q:a 2 {mp3_path} 2>/dev/null")
    if ret == 0 and os.path.exists(mp3_path):
        os.remove(wav_path)
        return mp3_path
    return wav_path


def synthesize(text: str, output_path: str,
               voice: str = "茉莉",
               model: str = "mimo-v2.5-tts",
               style: str = "",
               fmt: str = "wav",
               optimize_preview: bool = False,
               stream: bool = False) -> str:
    """Call MiMo V2.5 TTS via OpenAI-compatible API."""
    api_key = os.environ.get("XIAOMI_API_KEY") or os.environ.get("MIMO_API_KEY")
    if not api_key:
        env_path = os.path.expanduser("~/.hermes/.env")
        if os.path.exists(env_path):
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("XIAOMI_API_KEY=") and not line.startswith("#"):
                        api_key = line.split("=", 1)[1]
                        break
    if not api_key:
        print("ERROR: XIAOMI_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    client = OpenAI(api_key=api_key, base_url="https://api.xiaomimimo.com/v1")

    # Build messages: user (style/director) → assistant (text)
    messages = []
    messages.append({"role": "user", "content": style or ""})
    messages.append({"role": "assistant", "content": text})

    # Build audio config
    audio_config = {"format": fmt}
    if model != "mimo-v2.5-tts-voicedesign":
        audio_config["voice"] = voice
    if model == "mimo-v2.5-tts-voicedesign" and optimize_preview:
        audio_config["optimize_text_preview"] = True

    kwargs = {
        "model": model,
        "messages": messages,
        "audio": audio_config,
    }
    if stream:
        kwargs["stream"] = True

    try:
        completion = client.chat.completions.create(**kwargs)
    except Exception as e:
        print(f"ERROR: API call failed: {e}", file=sys.stderr)
        sys.exit(1)

    if stream:
        import numpy as np
        collected = np.array([], dtype=np.float32)
        for chunk in completion:
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta
            audio = getattr(delta, "audio", None)
            if audio is not None and isinstance(audio, dict) and "data" in audio:
                pcm = np.frombuffer(base64.b64decode(audio["data"]), dtype=np.int16).astype(np.float32) / 32768.0
                collected = np.concatenate((collected, pcm))
        if len(collected) == 0:
            print("ERROR: No audio data received in stream", file=sys.stderr)
            sys.exit(1)
        try:
            import soundfile as sf
            sf.write(output_path, collected, samplerate=24000)
        except ImportError:
            # fallback: write raw PCM16
            raw = (collected * 32768.0).astype(np.int16).tobytes()
            with open(output_path, "wb") as f:
                f.write(raw)
        print(f"OK (streamed): {len(collected)} samples written to {output_path}", file=sys.stderr)
    else:
        # Non-stream: extract audio from the final message
        try:
            message = completion.choices[0].message
            if not message.audio or not message.audio.data:
                raise KeyError("No audio data in response")
            audio_bytes = base64.b64decode(message.audio.data)
        except (KeyError, IndexError, AttributeError) as e:
            import json
            body = completion.model_dump() if hasattr(completion, "model_dump") else str(completion)
            print(f"ERROR: Response format: {body[:500]}", file=sys.stderr)
            sys.exit(1)

        with open(output_path, "wb") as f:
            f.write(audio_bytes)

    # Convert to MP3 if requested
    if fmt == "mp3" and output_path.endswith(".wav"):
        output_path = _to_mp3(output_path)

    print(f"OK: {os.path.getsize(output_path)} bytes written to {output_path}", file=sys.stderr)

    return output_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Xiaomi MiMo V2.5 TTS adapter")
    parser.add_argument("--text", help="Text to synthesize (assistant message)")
    parser.add_argument("--input-path", help="Read text from file")
    parser.add_argument("--output-path", required=True, help="Output audio path")
    parser.add_argument("--voice", default="茉莉", help="Voice name (e.g. 茉莉, Chloe, 冰糖, 苏打)")
    parser.add_argument("--model", default="mimo-v2.5-tts",
                        choices=["mimo-v2.5-tts", "mimo-v2.5-tts-voicedesign", "mimo-v2.5-tts-voiceclone"],
                        help="Model ID")
    parser.add_argument("--style", default="",
                        help="Natural-language style/director instruction (sent as user message)")
    parser.add_argument("--format", default="wav", choices=["wav", "mp3", "pcm16"],
                        help="Output audio format (mp3 requires ffmpeg, pcm16 for streaming)")
    parser.add_argument("--optimize-preview", action="store_true",
                        help="Auto-polish text (voicedesign model only)")
    parser.add_argument("--stream", action="store_true",
                        help="Enable streaming (format must be pcm16)")

    args = parser.parse_args()

    if args.text:
        text = args.text
    elif args.input_path:
        with open(args.input_path) as f:
            text = f.read()
    else:
        print("ERROR: --text or --input-path required", file=sys.stderr)
        sys.exit(1)

    synthesize(text, args.output_path, args.voice, args.model,
               args.style, args.format, args.optimize_preview, args.stream)
