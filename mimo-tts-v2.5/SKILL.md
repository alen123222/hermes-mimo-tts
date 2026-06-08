---
name: mimo-tts-v2.5
description: "Xiaomi MiMo V2.5 TTS — 非传统 TTS，而是语音表演模型。支持自然语言风格控制、导演模式（角色/场景/指导）、音频标签（情绪/气声/停顿）、音色设计、音色复刻。适配脚本位于 scripts/mimo_tts.py，Hermes 配置见 tts.providers.mimo.command"
version: 1.5.0
author: MiMo Team / Hermes OSS
---

# MiMo-V2.5-TTS 语音表演模型

**MiMo-V2.5-TTS 是一款语音表演模型**，它更像一位数字声优。模型能够理解复杂的自然语言指令来**表演**文本，支持多风格切换、复合情绪表现及字级细粒度气息控制。

## 🛠 环境预检（Prerequisites）

新 Agent clone 本仓库后，运行 TTS 前确保以下项就绪：

1. **API Key**：在 `~/.hermes/.env` 中放置 `XIAOMI_API_KEY="你的key"`，或设置环境变量 `XIAOMI_API_KEY`。
2. **Python 依赖**：`pip install openai numpy soundfile`
3. **ffmpeg**：`apt install -y ffmpeg`（用于 MP3 格式输出）
4. **运行脚本**：`scripts/mimo_tts.py` 是核心适配器，直接 `python3 scripts/mimo_tts.py --text "..." --output-path out.wav` 即可调用。

## 核心架构

```
── 输入流说明 ──
role: user     → 风格导演指令 (Style / Director Instruction)
role: assistant → 目标朗读文本与音频标签 (Content with Audio Tags)
──────────────────
audio: {format, voice} → 输出参数与基础音色
```

## 1. 风格导演指令 (Style Control)

通过自然语言描述控制整体播报基调。在 Hermes 环境中，这通常对应配置文件中的 `--style` 参数。

**推荐指令格式**：
> "用[语速]、[语气]的语气进行播报，发音[特征]，语句间留有[停顿感/气息感]。"

**中性示例**：
- "用专业且富有亲和力的语调，语速适中，发音清晰，适合正式场合的说明。"
- "冷静、低沉的播报风格，语速稍慢，重点突出文字的力量感。"

## 2. 音频标签控制 (Assistant Tags)

在目标文本中嵌入标签，可实现即时的情绪切换和动作表现。标签本身不会被朗读。

### A. 句首风格标签
在文本开头添加 `(风格)`。支持复合标签 `(风格1 风格2)`。
- **情绪类**：开心、悲伤、欣慰、从容、严肃、动情、忐忑。
- **语调类**：温柔、高冷、活泼、慵懒、俏皮、深沉。

**示例**：
- `(欣慰) 看到项目圆满完成，真是令人感叹。`
- `(严肃 沉稳) 接下来我们将讨论本次事故的根本原因。`

### B. 句中动作/气息标签
在文本中插入 `[标签]` 或 `（标签）` 以调节节奏。
- **节奏/气息**：`[吸气]` `[深呼吸]` `[叹气]` `[长叹一口气]` `[喘息]` `[停顿]`。
- **细微情绪**：`[轻笑]` `[苦笑]` `[哽咽]` `[破音]` `[沙哑]`。

**示例**：
- `(思索) 这个问题，[停顿] 恐怕我们需要更长的时间来评估。[叹气] 麻烦大家再确认一下数据。`

## 3. 音色设计模式 (Voicedesign)

使用 `mimo-v2.5-tts-voicedesign` 模型可通过纯文字描述定制新音色。

⚠️ **调用规范**：
- 该模型**不支持** `--voice` 参数。传入 voice 字段会导致 400 错误。
- 必须使用 `terminal()` 直接调用适配脚本 `scripts/mimo_tts.py`。
- 适配脚本已包含自动容错逻辑，但手动构造请求时请务必移除 voice 字段。

**调用示例**：
```bash
python3 scripts/mimo_tts.py \
  --model mimo-v2.5-tts-voicedesign \
  --text "欢迎来到智能语音实验室。" \
  --output-path /tmp/new_voice.mp3 \
  --format mp3 \
  --style "一个年轻且充满活力的男声，声音清脆，发音利落，带有自信感。"
```

## 4. 环境配置参考

**Hermes 默认配置示例**：
```bash
# 设置为 MP3 格式输出，并定义全局基础风格
hermes config set tts.providers.mimo.command "python3 scripts/mimo_tts.py --input-path {input_path} --output-path {output_path} --voice 茉莉 --model mimo-v2.5-tts --format mp3 --style '自然清晰的播报语气，语速平稳'"
```

## 5. 仓库脚本说明

适配脚本 `scripts/mimo_tts.py` 封装了 MiMo V2.5 的 OpenAI 兼容 API 调用，支持：
- **参数**：`--text`, `--input-path`, `--output-path`, `--voice`, `--model`, `--style`, `--format` (wav/mp3/pcm16), `--optimize-preview`, `--stream`
- **API Key 来源**：优先 `XIAOMI_API_KEY` 环境变量，其次 `~/.hermes/.env` 中的 `XIAOMI_API_KEY=` 行
- **依赖**：`openai` Python 包, `numpy` (流式模式), `soundfile` (流式模式), `ffmpeg` (mp3 输出)

## ⚠️ 常见陷阱与解决

1. **指令被朗读**：`text` 参数（assistant 消息）中除 `()` 和 `[]` 括起来的标签外，所有文字都会被模型读出。导演指令请务必放在 `--style`（user 消息）中。
2. **音色幼态化**：在描述少女/少年音色时，若关键词包含“可爱、撒娇”较多，易产生过于幼态的声音。建议添加“成熟度适中、发音标准”等修饰词。
3. **MP3 格式**：`--format mp3` 依赖服务器安装 `ffmpeg`。

## 模型列表

| 模型 ID | 功能说明 |
|---------|----------|
| `mimo-v2.5-tts` | 基础模型，使用预置精品音色（如：茉莉、冰糖、苏打）。 |
| `mimo-v2.5-tts-voicedesign` | 文本定制音色（无需样本）。 |
| `mimo-v2.5-tts-voiceclone` | 样本复刻音色。 |

## 📦 独立 Skill 仓库

本 Skill 已拆分为独立 Git 仓库，方便版本管理和共享：
- **MiMo TTS**: `https://github.com/alen123222/hermes-mimo-tts`

本地仍通过 `~/.hermes/skills/creative/mimo-tts-v2.5/` 目录访问。
