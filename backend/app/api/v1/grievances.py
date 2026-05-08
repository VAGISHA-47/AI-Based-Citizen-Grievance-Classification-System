from fastapi import APIRouter, BackgroundTasks, File, Form, UploadFile

from app.services.grievance_service import build_grievance_response, queue_grievance_ai


router = APIRouter(prefix="/api/v1", tags=["grievances-v1"])


@router.post("/complaints")
async def submit_complaint(
    title: str = Form(...),
    description: str = Form(...),
    channel: str = Form("web"),
    file: UploadFile | None = File(None),
    background_tasks: BackgroundTasks = None,
):
    grievance = build_grievance_response(title, description, channel, file)
    queue_grievance_ai(background_tasks, grievance["id"], title, description)
    return grievance


@router.post("/grievances/")
async def submit_grievance(
    title: str = Form(...),
    description: str = Form(...),
    channel: str = Form("web"),
    file: UploadFile | None = File(None),
    background_tasks: BackgroundTasks = None,
):
    grievance = build_grievance_response(title, description, channel, file)
    queue_grievance_ai(background_tasks, grievance["id"], title, description)
    return grievance