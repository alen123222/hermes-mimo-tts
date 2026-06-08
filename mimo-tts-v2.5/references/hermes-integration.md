# Hermes 集成配置（通用生产参考）

## 1. TTS Provider 配置模板

此配置适用于 Hermes `config.yaml`，定义了基础驱动逻辑。

```yaml
tts:
  provider: mimo
  providers:
    mimo:
      type: command
      command: >-
        /usr/local/bin/mimo_tts.py
        --input-path {input_path}
        --output-path {output_path}
        --voice 茉莉
        --model mimo-v2.5-tts
        --style '自然且清晰的播报语气，语速适中，适合作为默认助手音色'
      output_format: wav
      voice_compatible: true
```

## 2. 脚本参数参考

适配器脚本：`/usr/local/bin/mimo_tts.py`

| 参数 | 推荐默认值 | 作用 |
|------|-----------|------|
| `--text` | — | 待朗读文本（含表情/动作标签） |
| `--output-path` | 必填 | 音频存储路径 |
| `--voice` | `茉莉` | 仅适用于基础 TTS 模型 |
| `--style` | `""` | 发送给模型的导演风格指令 |
| `--format` | `mp3` | 推荐使用 mp3 以平衡体积与质量 |

## 3. 操作范例

### 场景 A：即时切换情绪
不需要修改全局配置，直接在对话文本中通过标签实现：
`text_to_speech(text="(从容) 您好，[吸气] 欢迎访问我们的服务系统。")`

### 场景 B：修改全局默认风格
通过指令快速更新 Agent 播报的基础语调：
```bash
hermes config set tts.providers.mimo.command "... --style '沉稳专业的商务播报风，语速平稳'"
```

### 场景 C：定制化音色开发 (Voicedesign)
用于实验性创建新音色：
```bash
/usr/local/bin/mimo_tts.py \
  --model mimo-v2.5-tts-voicedesign \
  --text "这是一个通过文本描述生成的新音色测试。" \
  --output-path /tmp/new_sample.mp3 \
  --format mp3 \
  --style "冷静、中性的成年男声，发音略带磁性"
```
