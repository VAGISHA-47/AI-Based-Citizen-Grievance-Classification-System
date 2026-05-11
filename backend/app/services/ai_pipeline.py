import os
import httpx

AI_ENGINE_URL = os.getenv("AI_ENGINE_URL", "http://localhost:8001")
_TIMEOUT = 30.0


def _endpoint(path: str) -> str:
    return f"{AI_ENGINE_URL.rstrip('/')}{path}"


async def check_ai_engine_health() -> tuple[bool, str]:
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(_endpoint("/health"))
        if response.status_code != 200:
            return False, f"status={response.status_code} body={response.text[:200]}"
        data = response.json()
        if data.get("status") != "ok":
            return False, f"unexpected-health-payload={data}"
        if not data.get("ready"):
            return False, f"ai-engine-not-ready: {data}"
        return True, "ok"
    except Exception as e:
        return False, str(e)

def classify_text(text: str) -> dict:
    try:
        with httpx.Client(timeout=_TIMEOUT) as client:
            response = client.post(_endpoint("/classify"), data={"text": text})
        response.raise_for_status()
        data = response.json()
        return {
            "category": str(data.get("category", "General")),
            "priority": str(data.get("priority", "Medium")),
            "sla_days": float(data.get("sla_days", 5.0)),
        }
    except Exception as e:
        print(f"[AI-PROXY] classify_text error: {e}")
        return {"category": "General", "priority": "Medium", "sla_days": 5.0}


def verify_image(text: str, image_bytes: bytes) -> dict:
    try:
        files = {
            "file": ("image.jpg", image_bytes, "application/octet-stream"),
        }
        with httpx.Client(timeout=_TIMEOUT) as client:
            response = client.post(_endpoint("/verify-image"), data={"text": text}, files=files)
        response.raise_for_status()
        data = response.json()
        return {
            "verified": bool(data.get("verified", True)),
            "score": float(data.get("score", 0.0)),
            "reason": str(data.get("reason", "Image verification completed")),
        }
    except Exception as e:
        print(f"[AI-PROXY] verify_image error: {e}")
        return {"verified": True, "score": 0.0, "reason": str(e)}


def transcribe_audio(audio_path: str) -> dict:
    try:
        with open(audio_path, "rb") as f:
            files = {
                "file": (os.path.basename(audio_path) or "audio.wav", f, "application/octet-stream"),
            }
            with httpx.Client(timeout=120.0) as client:
                response = client.post(_endpoint("/transcribe"), files=files)
        response.raise_for_status()
        data = response.json()
        return {
            "transcript": str(data.get("transcript", "")),
            "success": bool(data.get("success", False)),
            **({"error": str(data.get("error"))} if data.get("error") else {}),
        }

    except Exception as e:
        print(f"[AI-PROXY] transcribe_audio error: {e}")
        return {
            "transcript": "",
            "success": False,
            "error": str(e)
        }
