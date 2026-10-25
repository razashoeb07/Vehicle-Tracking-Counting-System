from sqlalchemy.orm import Session
from backend.app.database.models import Video, VehicleCount


def save_video_results(
    db: Session,
    filename: str,
    down_counts: dict,
    up_counts: dict,
    metadata: dict = None
):
    metadata = metadata or {}

    video = Video(
        filename=filename,
        status="completed",
        duration=metadata.get("duration"),
        fps=metadata.get("fps"),
        resolution=metadata.get("resolution"),
    )

    db.add(video)
    db.flush()

    for vehicle_type, count in down_counts.items():
        db.add(
            VehicleCount(
                video_id=video.id,
                vehicle_type=vehicle_type,
                direction="down",
                count=count,
            )
        )

    for vehicle_type, count in up_counts.items():
        db.add(
            VehicleCount(
                video_id=video.id,
                vehicle_type=vehicle_type,
                direction="up",
                count=count,
            )
        )

    db.commit()
    db.refresh(video)

    return video