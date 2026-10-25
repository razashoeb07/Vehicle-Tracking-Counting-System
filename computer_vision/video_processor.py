import cv2
import time

from tracker import VehicleTracker
from counter import VehicleCounter


class VideoProcessor:

    def __init__(
        self,
        input_path,
        output_path=None,
        red_line_y=200,
        blue_line_y=300,
        frame_callback=None
    ):
        self.input_path = input_path
        self.output_path = output_path
        self.frame_callback = frame_callback

        self.red_line_y = red_line_y
        self.blue_line_y = blue_line_y

        self.tracker = VehicleTracker()
        self.class_list = self.tracker.class_names

        self.counter = VehicleCounter(
            red_line_y=self.red_line_y,
            blue_line_y=self.blue_line_y
        )

        # Video metadata
        self.metadata = {}

    def process(self):

        cap = cv2.VideoCapture(self.input_path)

        if not cap.isOpened():
            raise ValueError(
                f"Could not open video: {self.input_path}"
            )

        frame_width = int(
            cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        )

        frame_height = int(
            cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        )

        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(
            cap.get(cv2.CAP_PROP_FRAME_COUNT)
        )

        # Calculate video metadata
        duration = (
            total_frames / fps
            if fps and fps > 0
            else None
        )

        self.metadata = {
            "duration": duration,
            "fps": fps if fps > 0 else None,
            "resolution": f"{frame_width}x{frame_height}",
        }

        writer = None

        if self.output_path:

            fourcc = cv2.VideoWriter_fourcc(*"mp4v")

            writer = cv2.VideoWriter(
                self.output_path,
                fourcc,
                fps if fps > 0 else 25.0,
                (frame_width, frame_height)
            )

            if not writer.isOpened():
                cap.release()
                raise ValueError(
                    f"Could not create output video: {self.output_path}"
                )

        try:
            while cap.isOpened():

                ret, frame = cap.read()

                if not ret:
                    break

                results = self.tracker.track(frame)

                # RED line
                cv2.line(
                    frame,
                    (0, self.red_line_y),
                    (frame_width, self.red_line_y),
                    (0, 0, 255),
                    3
                )

                cv2.putText(
                    frame, "RED LINE",
                    (10, self.red_line_y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7, (0, 0, 255), 2, cv2.LINE_AA
                )

                # BLUE line
                cv2.line(
                    frame,
                    (0, self.blue_line_y),
                    (frame_width, self.blue_line_y),
                    (255, 0, 0),
                    3
                )

                cv2.putText(
                    frame, "BLUE LINE",
                    (10, self.blue_line_y - 10),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7, (255, 0, 0), 2, cv2.LINE_AA
                )

                # Process detections
                if (
                    results[0].boxes.data is not None
                    and results[0].boxes.id is not None
                ):
                    boxes = results[0].boxes.xyxy.cpu()

                    track_ids = (
                        results[0].boxes.id.int().cpu().tolist()
                    )

                    class_indices = (
                        results[0].boxes.cls.int().cpu().tolist()
                    )

                    for box, track_id, class_idx in zip(
                        boxes, track_ids, class_indices
                    ):
                        x1, y1, x2, y2 = map(int, box)

                        cx = (x1 + x2) // 2
                        cy = (y1 + y2) // 2

                        class_name = self.class_list[class_idx]

                        self.counter.update(
                            track_id, class_name, cy
                        )

                        cv2.circle(
                            frame, (cx, cy), 4, (0, 0, 255), -1
                        )

                        cv2.rectangle(
                            frame,
                            (x1, y1), (x2, y2),
                            (0, 255, 0), 2
                        )

                        cv2.putText(
                            frame,
                            f"ID: {track_id} | {class_name}",
                            (x1, max(y1 - 10, 20)),
                            cv2.FONT_HERSHEY_SIMPLEX,
                            0.6, (0, 255, 255), 2, cv2.LINE_AA
                        )

                # Get counts
                count_red_to_blue, count_blue_to_red = (
                    self.counter.get_counts()
                )

                # DOWN counts
                y_offset = 30

                for class_name, count in count_red_to_blue.items():
                    text = f"{class_name.upper()} DOWN: {count}"

                    cv2.rectangle(
                        frame,
                        (5, y_offset - 25),
                        (250, y_offset + 5),
                        (0, 0, 0), -1
                    )

                    cv2.putText(
                        frame, text,
                        (10, y_offset),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7, (255, 255, 255), 2, cv2.LINE_AA
                    )

                    y_offset += 35

                # UP counts
                y_offset += 20

                for class_name, count in count_blue_to_red.items():
                    text = f"{class_name.upper()} UP: {count}"

                    cv2.rectangle(
                        frame,
                        (5, y_offset - 25),
                        (250, y_offset + 5),
                        (0, 0, 0), -1
                    )

                    cv2.putText(
                        frame, text,
                        (10, y_offset),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7, (255, 255, 255), 2, cv2.LINE_AA
                    )

                    y_offset += 35

                if writer:
                    writer.write(frame)

                # Send processed frame to the dashboard if callback is provided
                if self.frame_callback is not None:
                    count_data = {
                        "down": dict(count_red_to_blue),
                        "up": dict(count_blue_to_red),
                    }

                    self.frame_callback(frame.copy(), count_data)

                cv2.imshow(
                    "Vehicle Tracking & Counting", frame
                )

                if cv2.waitKey(1) & 0xFF == 27:
                    break

        finally:
            cap.release()

            if writer:
                writer.release()

            cv2.destroyAllWindows()

        return self.counter.get_counts()