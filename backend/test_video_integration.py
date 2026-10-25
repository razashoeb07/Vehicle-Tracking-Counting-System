
import sys
from pathlib import Path

# Project root directory
ROOT_DIR = Path(__file__).resolve().parent.parent

# Allow Python to import detector, tracker, counter and video_processor
COMPUTER_VISION_DIR = ROOT_DIR / "computer_vision"
sys.path.insert(0, str(COMPUTER_VISION_DIR))

from video_processor import VideoProcessor
from backend.app.database.connection import SessionLocal
from backend.app.services.video_service import save_video_results


def main():
    video_path_input = input(
        "Enter input video path (e.g. input/traffic.mp4): "
    ).strip().strip('"')

    input_path = Path(video_path_input)

    if not input_path.is_absolute():
        input_path = ROOT_DIR / input_path

    if not input_path.is_file():
        print(f"ERROR: Video file not found: {input_path}")
        return

    output_dir = ROOT_DIR / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / f"processed_{input_path.name}"

    db = SessionLocal()

    try:
        print("\nStarting vehicle detection and counting...")

        processor = VideoProcessor(
            input_path=str(input_path),
            output_path=str(output_path),
            red_line_y=200,
            blue_line_y=300,
        )

        # Returns: (red_to_blue_counts, blue_to_red_counts)
        down_counts, up_counts = processor.process()
        metadata = processor.metadata
        print("Video metadata:", metadata)

        print("\nVideo processing completed.")
        print("DOWN counts:", down_counts)
        print("UP counts:", up_counts)

        video = save_video_results(
            db=db,
            filename=input_path.name,
            down_counts=down_counts,
            up_counts=up_counts,
            metadata=metadata
        )

        print("\nDatabase save successful!")
        print(f"Video ID: {video.id}")
        print(f"Processed video: {output_path}")

    except Exception as error:
        db.rollback()
        print(f"\nIntegration failed: {error}")
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()
