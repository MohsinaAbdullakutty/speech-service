from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from faster_whisper import WhisperModel
import tempfile
import os
import time

app = FastAPI(title="Whisper STT Service")

# ---------------------------------------------------
# Load model ONCE when the application starts
# ---------------------------------------------------

MODEL_NAME = os.getenv("WHISPER_MODEL", "base")

model = WhisperModel(
    MODEL_NAME,
    device="cpu",
    compute_type="int8",
    cpu_threads=4
)


@app.get("/health")
def health():
    return {
        "status": "UP",
        "model": MODEL_NAME
    }


@app.post("/transcribe")
async def transcribe(
    file: UploadFile = File(...),
    language: str = Form(None)
):
    start_time = time.time()

    filename = file.filename or "audio.wav"
    suffix = os.path.splitext(filename)[1] or ".wav"

    with tempfile.NamedTemporaryFile(
        delete=False,
        suffix=suffix
    ) as temp:

        temp.write(await file.read())
        temp_path = temp.name

    try:

        selected_language = None

        if language:
            language = language.lower().strip()

            if language in ["ar", "arabic"]:
                selected_language = "ar"

            elif language in ["en", "english"]:
                selected_language = "en"

        #
        # Domain-specific terms help recognition.
        #
        if selected_language == "ar":

            prompt = (
                "السفن، الميناء، المرفأ، المنطقة المحظورة، "
                "منطقة الصيد، المخالفات، السرعة، المسار، "
                "AIS, MMSI, IUU, Port Rashid, Deira"
            )

        else:

            prompt = (
                "Maritime vessel tracking. "
                "AIS, MMSI, vessel, vessels, ship, harbour, harbor, "
                "port, Port Rashid, Deira, restricted area, "
                "restricted zone, fishing block, fishing area, "
                "IUU, violation, speed, course."
            )

        segments, info = model.transcribe(

            temp_path,

            # Force Arabic / English whenever frontend knows it
            language=selected_language,

            # IMPORTANT:
            # much faster than beam_size=5
            beam_size=1,

            # Remove silence before transcription
            vad_filter=True,

            vad_parameters={
                "min_silence_duration_ms": 300
            },

            # Helps maritime terminology
            initial_prompt=prompt,

            # Better for independent chatbot commands
            condition_on_previous_text=False
        )

        text = " ".join(
            segment.text.strip()
            for segment in segments
            if segment.text.strip()
        )

        processing_time = round(time.time() - start_time, 2)

        return {
            "text": text,
            "language": info.language,
            "languageProbability": getattr(
                info,
                "language_probability",
                None
            ),
            "duration": info.duration,
            "processingTimeSeconds": processing_time,
            "model": MODEL_NAME
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:

        if os.path.exists(temp_path):
            os.remove(temp_path)