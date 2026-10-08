# Local Piper TTS service

This project uses Piper's own HTTP server as the private text-to-speech service. It keeps the voice models loaded/cached, which is better for repeated chatbot responses than starting the Piper CLI for every answer.

## 1. Download the voices once
From inside `tts-service/models` (or another model directory), install Piper and download:

```bash
pip install "piper-tts[http]==1.8.0"
python -m piper.download_voices en_US-lessac-medium ar_JO-kareem-medium
```

Piper voices use an `.onnx` model plus a matching `.onnx.json` config. Review each voice model's model card/license before deployment.

## 2. Run with Docker

```bash
docker build -t vessel-piper-tts ./tts-service
docker run --rm -p 9026:9026 -v "${PWD}/tts-service/models:/models" vessel-piper-tts
```

Piper's HTTP server is then available on port `9026`.

Check downloaded voices:

```bash
curl http://localhost:9026/voices
```

Direct English test:

```bash
curl -X POST http://localhost:9026/synthesize \
  -H "Content-Type: application/json" \
  -d '{"text":"I found three vessels in restricted areas.","voice":"en_US-lessac-medium"}' \
  --output answer.wav
```

Direct Arabic test:

```bash
curl -X POST http://localhost:9026/synthesize \
  -H "Content-Type: application/json" \
  -d '{"text":"تم العثور على ثلاث سفن في المناطق المحظورة.","voice":"ar_JO-kareem-medium"}' \
  --output answer-ar.wav
```

## 3. Through vessel-service
The Spring Boot service exposes:

`POST /api/ai/speak`

Body:

```json
{"text":"I found three vessels in restricted areas.","language":"en"}
```

Arabic:

```json
{"text":"تم العثور على ثلاث سفن في المناطق المحظورة.","language":"ar"}
```

The endpoint returns `audio/wav`. `language` may also be `auto`; the Java service detects Arabic script and selects the configured Arabic voice.

The existing `/api/ai/ask` and `/api/ai/voice` response formats are unchanged. The UI should take `response.answer` and call `/api/ai/speak` when it wants to play the answer.

## Configuration

```yaml
ai:
  tts:
    url: ${AI_TTS_URL:http://localhost:9026/synthesize}
    max-text-chars: 2000
    voices:
      en: ${AI_TTS_VOICE_EN:en_US-lessac-medium}
      ar: ${AI_TTS_VOICE_AR:ar_JO-kareem-medium}
```

If `vessel-service` itself runs in Docker, set `AI_TTS_URL` to the TTS container/service hostname instead of `localhost`.
