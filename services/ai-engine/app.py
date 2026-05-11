from __future__ import annotations

import io
import os
import pickle
import tempfile
from pathlib import Path

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI(title="JanSetu AI Engine", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ROOT_DIR = Path(__file__).resolve().parent
WEIGHTS_DIR = ROOT_DIR / "weights"

clip_model = None
clip_processor = None
whisper_model = None
vectorizer = None
classifier_model = None
priority_model = None
sla_model = None


def _load_whisper_model():
    global whisper_model
    if whisper_model is not None:
        return whisper_model
    import whisper

    whisper_model = whisper.load_model("base")
    return whisper_model


def _load_clip_models():
    global clip_model, clip_processor
    if clip_model is not None and clip_processor is not None:
        return clip_model, clip_processor

    from transformers import CLIPModel, CLIPProcessor

    clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
    clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
    return clip_model, clip_processor


def _load_text_models():
    global vectorizer, classifier_model, priority_model, sla_model
    if vectorizer is not None and classifier_model is not None:
        return

    with open(WEIGHTS_DIR / "vectorizer.pkl", "rb") as f:
        vectorizer = pickle.load(f)
    with open(WEIGHTS_DIR / "classifier.pkl", "rb") as f:
        classifier_model = pickle.load(f)

    priority_path = WEIGHTS_DIR / "priority_classifier.pkl"
    if priority_path.exists():
        with open(priority_path, "rb") as f:
            priority_model = pickle.load(f)

    sla_path = WEIGHTS_DIR / "sla_model.pkl"
    if sla_path.exists():
        with open(sla_path, "rb") as f:
            sla_model = pickle.load(f)


@app.on_event("startup")
async def startup_event():
    # Attempt to eagerly load all trained models so the service is ready
    print("[AI-ENGINE] Service starting on port 8001 — loading models...")
    errors = []
    global clip_model, clip_processor, whisper_model, vectorizer, classifier_model, sla_model, priority_model
    text_ok = False
    whisper_ok = False
    clip_ok = False
    try:
        _load_text_models()
        text_ok = True
        print("[AI-ENGINE] Text models loaded")
    except Exception as e:
        errors.append(f"text_models:{e}")

    try:
        _load_clip_models()
        clip_ok = True
        print("[AI-ENGINE] CLIP model loaded")
    except Exception as e:
        errors.append(f"clip:{e}")

    try:
        _load_whisper_model()
        whisper_ok = True
        print("[AI-ENGINE] Whisper model loaded")
    except Exception as e:
        errors.append(f"whisper:{e}")

    # Require text models and whisper for the service to be considered ready
    if text_ok and whisper_ok:
        app.state.models_ready = True
        print("[AI-ENGINE] Required models loaded — service ready")
        if clip_ok:
            print("[AI-ENGINE] CLIP available")
    else:
        print(f"[AI-ENGINE] Model load errors: {errors}")
        app.state.models_ready = False


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "service": "ai-engine",
        "ready": bool(getattr(app.state, "models_ready", False)),
    }


@app.post("/classify")
async def classify(text: str = Form(...)):
    try:
        _load_text_models()
        vec = vectorizer.transform([text])
        category = str(classifier_model.predict(vec)[0])
        priority = "Medium"
        if priority_model is not None:
            try:
                priority = str(priority_model.predict(vec)[0])
            except Exception:
                priority = "Medium"
        sla_days = 5.0
        if sla_model is not None:
            try:
                sla_days = float(sla_model.predict(vec)[0])
            except Exception:
                sla_days = 5.0

        return {
            "category": category,
            "priority": priority,
            "sla_days": round(sla_days, 1),
        }
    except Exception as e:
        print(f"[AI-ENGINE] classify error: {e}")
        return {
            "category": "General",
            "priority": "Medium",
            "sla_days": 5.0,
            "error": str(e),
        }


@app.post("/verify-image")
async def verify_image(text: str = Form(...), file: UploadFile = File(...)):
    try:
        import torch
        from PIL import Image

        model, processor = _load_clip_models()
        image_data = await file.read()
        image = Image.open(io.BytesIO(image_data)).convert("RGB")
        inputs = processor(
            text=[f"a photo of {text}", "a random unrelated photo"],
            images=image,
            return_tensors="pt",
            padding=True,
        )

        with torch.no_grad():
            outputs = model(**inputs)
        probs = outputs.logits_per_image.softmax(dim=1)
        score = float(probs[0][0].item())
        if score < 0.6:
            return {
                "verified": False,
                "score": round(score, 3),
                "reason": "Image does not match description",
            }
        return {
            "verified": True,
            "score": round(score, 3),
            "reason": "Image verified",
        }
    except Exception as e:
        print(f"[AI-ENGINE] verify-image error: {e}")
        return {
            "verified": True,
            "score": 0.0,
            "reason": str(e),
            "error": str(e),
        }


@app.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    suffix = Path(file.filename or "audio.wav").suffix or ".wav"
    tmp_path = None
    try:
        model = _load_whisper_model()
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name
        result = model.transcribe(tmp_path, fp16=False)
        transcript = result.get("text", "").strip()
        return {"transcript": transcript, "success": True}
    except Exception as e:
        print(f"[AI-ENGINE] transcribe error: {e}")
        return {"transcript": "", "success": False, "error": str(e)}
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)


@app.post("/predict")
async def predict_complaint(text: str = Form(...), file: UploadFile = File(...)):
    verify = await verify_image(text=text, file=file)
    classify_result = await classify(text=text)
    return {
        "verification": verify,
        "analysis": classify_result,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)