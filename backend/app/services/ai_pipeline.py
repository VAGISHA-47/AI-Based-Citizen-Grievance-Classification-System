import pickle
import os
import io
import torch
from PIL import Image
from transformers import CLIPProcessor, CLIPModel

BASE_DIR = os.path.join(os.path.dirname(__file__), "..", "ml")
WEIGHTS_DIR = os.path.join(BASE_DIR, "weights")

_vectorizer = None
_classifier = None
_priority_classifier = None
_sla_model = None
_clip_model = None
_clip_processor = None

def _load_pkl_models():
    global _vectorizer, _classifier, _priority_classifier, _sla_model
    try:
        with open(os.path.join(WEIGHTS_DIR, "vectorizer.pkl"), "rb") as f:
            _vectorizer = pickle.load(f)
        with open(os.path.join(WEIGHTS_DIR, "classifier.pkl"), "rb") as f:
            _classifier = pickle.load(f)
        with open(os.path.join(WEIGHTS_DIR, "priority_classifier.pkl"), "rb") as f:
            _priority_classifier = pickle.load(f)
        with open(os.path.join(WEIGHTS_DIR, "sla_model.pkl"), "rb") as f:
            _sla_model = pickle.load(f)
        print("[AI] Custom models loaded successfully")
    except Exception as e:
        print(f"[AI] Custom model loading failed: {e}")

def _load_clip():
    global _clip_model, _clip_processor
    try:
        print("[AI] Loading CLIP model...")
        _clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        _clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        print("[AI] CLIP loaded successfully")
    except Exception as e:
        print(f"[AI] CLIP loading failed: {e}")

_load_pkl_models()
_load_clip()

def classify_text(text: str) -> dict:
    try:
        if _vectorizer is None or _classifier is None:
            return {"category": "General", "priority": "Medium", "sla_days": 5.0}
        vec = _vectorizer.transform([text])
        category = _classifier.predict(vec)[0]
        priority = _priority_classifier.predict(vec)[0] if _priority_classifier else "Medium"
        sla_days = 5.0
        if _sla_model:
            try:
                sla_days = float(_sla_model.predict(vec)[0])
            except:
                sla_days = 5.0
        return {
            "category": str(category),
            "priority": str(priority),
            "sla_days": round(sla_days, 1)
        }
    except Exception as e:
        print(f"[AI] classify_text error: {e}")
        return {"category": "General", "priority": "Medium", "sla_days": 5.0}

def verify_image(text: str, image_bytes: bytes) -> dict:
    try:
        if _clip_model is None:
            return {"verified": True, "score": 0.0, "reason": "CLIP not loaded"}
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        inputs = _clip_processor(
            text=[f"a photo of {text}", "a random unrelated photo"],
            images=image,
            return_tensors="pt",
            padding=True
        )
        with torch.no_grad():
            outputs = _clip_model(**inputs)
        probs = outputs.logits_per_image.softmax(dim=1)
        score = probs[0][0].item()
        if score < 0.6:
            return {"verified": False, "score": round(score, 3), "reason": "Image does not match description"}
        return {"verified": True, "score": round(score, 3), "reason": "Image verified"}
    except Exception as e:
        print(f"[AI] verify_image error: {e}")
        return {"verified": True, "score": 0.0, "reason": str(e)}

def transcribe_audio(audio_path: str) -> dict:
    try:
        import whisper
        model = whisper.load_model("base")
        result = model.transcribe(audio_path, fp16=False)
        return {"transcript": result["text"], "success": True}
    except Exception as e:
        print(f"[AI] transcribe error: {e}")
        return {"transcript": "", "success": False}
