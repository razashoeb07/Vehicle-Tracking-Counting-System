import shutil
import uuid
import threading
from backend.app.live_state import live_state
from pathlib import Path

import cv2
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from backend.app.database.connection import SessionLocal
from backend.app.database.models import Video, VehicleCount
from backend.app.services.video_service import save_video_results

from fastapi.responses import Response
from backend.app.live_state import live_state

# Project root directory
ROOT_DIR = Path(__file__).resolve().parents[2]
UPLOAD_DIR = ROOT_DIR / "uploads"
OUTPUT_DIR = ROOT_DIR / "output"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv"}

app = FastAPI(
    title="Vehicle Tracking & Counting API",
    description="API for vehicle detection and counting results",
    version="1.0.0",
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def home():
    return {"message": "Vehicle Tracking API is running"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/videos")
def get_videos(db: Session = Depends(get_db)):
    videos = db.query(Video).order_by(Video.id.desc()).all()

    return [
        {
            "id": video.id,
            "filename": video.filename,
            "status": video.status,
            "uploaded_at": video.uploaded_at,
            "duration": video.duration,
            "fps": video.fps,
            "resolution": video.resolution,
        }
        for video in videos
    ]


@app.get("/videos/{video_id}/counts")
def get_video_counts(
    video_id: int,
    db: Session = Depends(get_db),
):
    video = db.query(Video).filter(Video.id == video_id).first()

    if video is None:
        raise HTTPException(status_code=404, detail="Video not found")

    counts = (
        db.query(VehicleCount)
        .filter(VehicleCount.video_id == video_id)
        .order_by(VehicleCount.direction, VehicleCount.vehicle_type)
        .all()
    )

    return {
        "video_id": video.id,
        "filename": video.filename,
        "status": video.status,
        "counts": [
            {
                "vehicle_type": item.vehicle_type,
                "direction": item.direction,
                "count": item.count,
            }
            for item in counts
        ],
    }


def process_video_in_background(input_path, output_path, original_filename):
    import sys

    db = None

    try:
        cv_dir = ROOT_DIR / "computer_vision"
        if str(cv_dir) not in sys.path:
            sys.path.insert(0, str(cv_dir))

        from video_processor import VideoProcessor

        # Background thread ke liye apna database session
        from backend.app.database.connection import SessionLocal
        db = SessionLocal()

        processor = VideoProcessor(
            input_path=str(input_path),
            output_path=str(output_path),
            red_line_y=200,
            blue_line_y=300,
            frame_callback=live_state.update_frame,
        )

        down_counts, up_counts = processor.process()
        metadata = processor.metadata

        video = save_video_results(
            db=db,
            filename=original_filename,
            down_counts=down_counts,
            up_counts=up_counts,
            metadata=metadata,
        )

        live_state.finish(status="completed")

    except Exception as error:
        if db is not None:
            db.rollback()

        output_path.unlink(missing_ok=True)
        live_state.finish(status="failed", error=str(error))

    finally:
        if db is not None:
            db.close()



@app.post("/videos/upload")
def upload_video(
    file: UploadFile = File(...),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is missing")

    extension = Path(file.filename).suffix.lower()

    if extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Unsupported format. Use MP4, AVI, MOV, or MKV.",
        )

    safe_filename = f"{uuid.uuid4().hex}{extension}"
    input_path = UPLOAD_DIR / safe_filename
    output_path = OUTPUT_DIR / f"processed_{safe_filename}"

    try:
        with input_path.open("wb") as destination:
            shutil.copyfileobj(file.file, destination)
    finally:
        file.file.close()

    cap = cv2.VideoCapture(str(input_path))

    if not cap.isOpened():
        cap.release()
        input_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is not a readable video.",
        )

    cap.release()

    # Reset the live state and start background processing.
    live_state.start()

    try:
        worker = threading.Thread(
            target=process_video_in_background,
            args=(input_path, output_path, file.filename),
            daemon=True,
        )
        worker.start()

    except Exception as error:
        live_state.finish(status="failed", error=str(error))
        input_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=500,
            detail=f"Could not start video processing: {str(error)}",
        )

    return {
        "message": "Video upload successful. Processing started.",
        "filename": file.filename,
        "status": "processing",
        "live_status_url": "/live/status",
        "live_frame_url": "/live/frame",
    }



@app.get("/live/status")
def get_live_status():
    snapshot = live_state.snapshot()

    return {
        "status": snapshot["status"],
        "counts": snapshot["counts"],
        "progress": snapshot["progress"],
        "error": snapshot["error"],
        "updated_at": snapshot["updated_at"],
    }


@app.get("/live/frame")
def get_live_frame():
    snapshot = live_state.snapshot()
    frame = snapshot["frame_jpeg"]

    if frame is None:
        return Response(status_code=204)

    return Response(
        content=frame,
        media_type="image/jpeg",
        headers={"Cache-Control": "no-cache"},
    )

