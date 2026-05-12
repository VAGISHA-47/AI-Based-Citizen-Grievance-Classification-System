import os
import shutil
import tempfile
import subprocess
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, UploadFile, File, Form, BackgroundTasks, HTTPException, Request

from app.services.routing_engine import run_routing_engine
from app.services.geo_mapper import get_ward_from_coordinates
from app.services.token_generator import generate_tracking_token
from app.utils.auth import verify_token
from app.db.supabase_client import supabase


router = APIRouter(prefix="/grievances", tags=["grievances"])
TEMP_COMPLAINTS: dict[str, dict] = {}
GUEST_PASSWORD_HASH = "$2b$12$n.z8fpfNHSmQZG6X4RckU.uwK843JqTDB7QSHcv2mzhMCRHypQHM2"
CATEGORY_CODES = {
    "Roads": "ROADS",
    "Water Supply": "WATER",
    "Electricity": "ELEC",
    "Sanitation": "SAN",
    "Parks & Recreation": "PARKS",
    "Health": "HEALTH",
    "Traffic": "TRF",
    "Drainage": "DRN",
    "General": "GEN",
}


def _resolve_user_id(auth_header: str | None, citizen_phone: str, citizen_name: str) -> str:
    """Resolve a valid users.user_id for complaint persistence."""
    from app.db.supabase_client import supabase

    def _lookup_user(field: str, value: str) -> str | None:
        if not value:
            return None
        result = supabase.table("users").select("user_id").eq(field, value).limit(1).execute()
        if result.data:
            return str(result.data[0]["user_id"])
        return None

    token = ""
    if auth_header and auth_header.lower().startswith("bearer "):
        token = auth_header.split(" ", 1)[1].strip()

    if token:
        payload = verify_token(token)
        if payload:
            identifier = payload.get("sub") or ""
            resolved = _lookup_user("email", identifier) or _lookup_user("phone", identifier)
            if resolved:
                return resolved

    resolved = _lookup_user("phone", citizen_phone) or _lookup_user("email", citizen_phone)
    if resolved:
        return resolved

    guest_phone = citizen_phone or "anonymous"
    guest_name = citizen_name or "Citizen"
    guest_result = supabase.table("users").insert({
        "phone": guest_phone,
        "email": f"{guest_phone}@guest.local" if guest_phone != "anonymous" else "anonymous@guest.local",
        "name": guest_name,
        "password_hash": GUEST_PASSWORD_HASH,
        "role": "citizen",
        "trust_score": 50,
        "trust_level": "new",
        "is_verified": False,
    }).execute()

    if guest_result.data:
        return str(guest_result.data[0]["user_id"])

    raise HTTPException(status_code=500, detail="Unable to resolve a user record for complaint submission")



@router.post("/")
async def submit_grievance(
    background_tasks: BackgroundTasks,
    title: str = Form(None),
    description: str = Form(None),
    category: str = Form(None),
    citizen_name: str = Form(None),
    citizen_phone: str = Form(None),
    lat: float = Form(19.076),
    lng: float = Form(72.877),
    address: str = Form(None),
    language_code: str = Form("en"),
    transcript: str = Form(None),
    file: UploadFile = File(None),
):
    try:
        # Use transcript as description if provided
        final_description = transcript or description or title or "No description"
        final_title = title or category or "General Complaint"

        # AI classification
        ai_result = {
            "category": category or "General",
            "priority": "medium",
            "sla_days": 5.0
        }
        clip_result = {"score": 0.0, "verified": True}

        try:
            from app.services.ai_pipeline import classify_text
            if final_description and final_description != "No description":
                ai_result = classify_text(final_description)
        except Exception as e:
            print(f"[AI] classify_text failed: {e}")

        # Use citizen category if provided, else AI
        final_category = category or ai_result.get("category", "General")

        CATEGORY_CODES = {
            "Roads": "ROADS",
            "Water Supply": "WATER",
            "Electricity": "ELEC",
            "Sanitation": "SAN",
            "Parks & Recreation": "PARKS",
            "Health": "HEALTH",
            "Traffic": "TRF",
            "Drainage": "DRN",
            "General": "GEN",
        }
        final_category_code = CATEGORY_CODES.get(final_category, "GEN")

        # Image verification
        image_bytes = None
        if file and file.filename:
            try:
                image_bytes = await file.read()
                from app.services.ai_pipeline import verify_image
                clip_result = verify_image(final_description, image_bytes)
            except Exception as e:
                print(f"[AI] verify_image failed: {e}")

        # Duplicate check
        try:
            from app.services.duplicate_service import check_duplicate
            dup = check_duplicate(final_description, final_category)
            if dup.get("is_duplicate"):
                return {
                    "status": "duplicate",
                    "message": "Similar complaint already exists",
                    "similarity": dup.get("similarity")
                }
        except Exception as e:
            print(f"[AI] duplicate check failed: {e}")

        # Generate tracking token
        from app.services.token_generator import generate_tracking_token
        from app.services.geo_mapper import get_ward_from_coordinates
        from app.services.sla_service import calculate_sla

        ward = get_ward_from_coordinates(lat, lng)
        tracking_token = generate_tracking_token(final_category, ward)
        sla_days = calculate_sla(
            final_category,
            ai_result.get("priority", "medium").upper()
        )

        # Save to Supabase
        insert_data = {
            "tracking_token": tracking_token,
            "text_original": final_description,
            "text_english": final_description,
            "language_code": language_code or "en",
            "category": final_category,
            "category_code": final_category_code,
            "priority": ai_result.get("priority", "medium"),
            "status": "submitted",
            "lat": lat,
            "lng": lng,
            "address": address or ward,
            "sla_days": sla_days,
            "ai_confidence": clip_result.get("score", 0.0),
        }

        result = supabase.table("complaints").insert(
            insert_data
        ).execute()

        if not result.data:
            raise Exception("Supabase insert returned no data")

        complaint_id = result.data[0]["complaint_id"]
        print(f"[GRIEVANCE] Saved: {tracking_token} | {final_category} | {final_description[:50]}")

        # Background routing
        background_tasks.add_task(
            _run_routing,
            complaint_id,
            {
                "description": final_description,
                "category": final_category,
                "priority": ai_result.get("priority", "MEDIUM").upper(),
                "sla_days": sla_days,
                "citizen_name": citizen_name or "Citizen",
                "citizen_phone": citizen_phone or "",
                "lat": lat,
                "lng": lng,
                "auth_score": clip_result.get("score", 0.0) * 100,
                "media_urls": [],
            }
        )

        return {
            "status": "success",
            "grievance_id": complaint_id,
            "tracking_token": tracking_token,
            "category": final_category,
            "sla_days": sla_days,
            "message": "Complaint submitted successfully"
        }

    except Exception as e:
        import traceback
        print(f"[GRIEVANCE ERROR] {type(e).__name__}: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Submission error: {str(e)}"
        )


async def _run_routing(grievance_id: str, data: dict):
    try:
        from app.services.routing_engine import run_routing_engine
        await run_routing_engine(grievance_id, data)
    except Exception as e:
        print(f"[ROUTING] Error: {e}")


@router.get("/track/{token}")
async def track_complaint(token: str):
    from app.db.supabase_client import supabase

    result = supabase.table("complaints").select("*").eq("tracking_token", token).execute()
    if result.data:
        return result.data[0]

    temp = TEMP_COMPLAINTS.get(token)
    if temp:
        return temp

    raise HTTPException(status_code=404, detail="Complaint not found")


@router.get("/my")
async def my_complaints():
    from app.db.supabase_client import supabase

    result = supabase.table("complaints").select(
        "complaint_id, tracking_token, status, category, created_at"
    ).order("created_at", desc=True).limit(10).execute()
    return result.data


@router.get("/queue")
async def queue_grievances(priority: str = None):
    """Fetch grievances for officer queue with optional priority filter."""
    from app.db.supabase_client import supabase
    
    try:
        query = supabase.table("complaints").select(
            "complaint_id, tracking_token, text_original, category, priority, status, created_at, lat, lng, sla_days, ai_confidence"
        ).order("created_at", desc=True)
        
        if priority and priority.lower() != "all":
            query = query.eq("priority", priority.lower())
        
        result = query.execute()
        
        # Format for officer queue UI
        formatted = []
        for item in result.data:
            formatted.append({
                "id": f"#CMP-{item['complaint_id'][-4:]}",
                "title": item["text_original"][:80] if item["text_original"] else "Unknown Issue",
                "cat": item["category"] or "General",
                "dept": "BBMP",  # can be enriched by routing engine later
                "citizen": "Citizen",  # can be added when auth is implemented
                "priority": item["priority"] or "medium",
                "slaHours": (item["sla_days"] or 5.0) * 24,
                "status": item["status"] or "submitted",
                "critical": (item["priority"] or "").lower() == "high",
                "tracking_token": item["tracking_token"],
            })
        
        return formatted
    except Exception as e:
        print(f"[ERROR] Failed to fetch grievances: {str(e)}")
        return []


@router.get("/test/token")
async def test_token():
    from app.services.token_generator import generate_tracking_token
    from app.services.sla_service import calculate_sla
    from app.services.geo_mapper import get_ward_from_coordinates, get_zone_room

    ward = get_ward_from_coordinates(19.12, 72.85)
    token = generate_tracking_token("Water Supply", ward)
    sla = calculate_sla("Water Supply", "HIGH")
    zone = get_zone_room(ward)
    return {"token": token, "ward": ward, "zone": zone, "sla_days": sla}


@router.post("/test/ai-classify")
async def test_classify(text: str = Form(...)):
    from app.services.ai_pipeline import classify_text
    result = classify_text(text)
    return {"input": text, "result": result}


@router.post("/test/ai-verify-image")
async def test_verify(text: str = Form(...), file: UploadFile = File(...)):
    from app.services.ai_pipeline import verify_image
    image_bytes = await file.read()
    result = verify_image(text, image_bytes)
    return {"input_text": text, "result": result}


@router.post("/test/ai-duplicate")
async def test_duplicate(text: str = Form(...), category: str = Form(...)):
    from app.services.duplicate_service import check_duplicate
    result = check_duplicate(text, category)
    return {"input": text, "result": result}


@router.post("/test/transcribe-audio")
async def transcribe_audio_route(
    file: UploadFile = File(...)
):
    from fastapi.responses import JSONResponse
    import tempfile, os, subprocess

    original_name = file.filename or "audio.webm"
    ext = os.path.splitext(original_name)[1] or ".webm"

    tmp_input = None
    tmp_wav = None

    try:
        # Save uploaded file
        with tempfile.NamedTemporaryFile(
            suffix=ext, delete=False
        ) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_input = tmp.name

        print(f"[TRANSCRIBE] Saved to: {tmp_input}")
        print(f"[TRANSCRIBE] File size: {os.path.getsize(tmp_input)} bytes")

        # Convert to wav
        tmp_wav = tmp_input.replace(ext, ".wav")
        try:
            subprocess.run([
                "ffmpeg", "-i", tmp_input,
                "-ar", "16000", "-ac", "1",
                "-f", "wav", tmp_wav,
                "-y", "-loglevel", "quiet"
            ], timeout=60, check=True)
            use_path = tmp_wav
            print(f"[TRANSCRIBE] Converted to WAV")
        except Exception as conv_err:
            print(f"[TRANSCRIBE] ffmpeg failed: {conv_err}, using original")
            use_path = tmp_input

        # Try whisper
        try:
            import whisper
        except ModuleNotFoundError:
            print("[TRANSCRIBE] Installing whisper...")
            import subprocess as sp, sys
            sp.run([
                sys.executable, "-m", "pip",
                "install", "openai-whisper", "-q"
            ], check=True, timeout=180)
            import whisper

        print("[TRANSCRIBE] Loading whisper model...")
        model = whisper.load_model("base")
        print("[TRANSCRIBE] Starting transcription (may take 30-60 seconds)...")
        result = model.transcribe(use_path, fp16=False)
        transcript = result.get("text", "").strip()
        print(f"[TRANSCRIBE] Success: {transcript[:80]}")

        return JSONResponse(
            {
                "transcript": transcript,
                "success": True
            },
            headers={
                "Connection": "keep-alive",
                "Cache-Control": "no-cache",
                "X-Accel-Buffering": "no"
            }
        )

    except Exception as e:
        print(f"[TRANSCRIBE] Error: {type(e).__name__}: {e}")
        return JSONResponse(
            {
                "transcript": "",
                "success": False,
                "error": str(e)
            },
            status_code=500,
            headers={
                "Connection": "keep-alive",
                "Cache-Control": "no-cache"
            }
        )
    finally:
        # Cleanup
        for path in [tmp_input, tmp_wav]:
            if path and os.path.exists(path):
                try:
                    os.unlink(path)
                except:
                    pass
