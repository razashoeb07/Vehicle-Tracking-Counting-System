from backend.app.database.connection import SessionLocal
from backend.app.services.video_service import save_video_results


db = SessionLocal()

try:
    video = save_video_results(
        db=db,
        filename="test_service.mp4",
        down_counts={
            "car": 5,
            "truck": 2
        },
        up_counts={
            "car": 1,
            "bus": 1
        }
    )

    print(f"Video saved successfully! ID: {video.id}")

finally:
    db.close()