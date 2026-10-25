import cv2

from tracker import VehicleTracker
from counter import VehicleCounter


# --------------------------------------------------
# 1. Load YOLO tracker
# --------------------------------------------------

tracker = VehicleTracker()

class_list = tracker.class_names


# --------------------------------------------------
# 2. Open video
# --------------------------------------------------

cap = cv2.VideoCapture("test_videos/3.mp4")


# --------------------------------------------------
# 3. Define counting lines
# --------------------------------------------------

line_y_red = 200
line_y_blue = 300


# --------------------------------------------------
# 4. Initialize vehicle counter
# --------------------------------------------------

counter = VehicleCounter(
    red_line_y=line_y_red,
    blue_line_y=line_y_blue
)


# --------------------------------------------------
# 5. Process video frame by frame
# --------------------------------------------------

while cap.isOpened():

    ret, frame = cap.read()

    if not ret:
        break


    # --------------------------------------------------
    # Get actual frame width
    # --------------------------------------------------

    frame_width = frame.shape[1]


    # --------------------------------------------------
    # Run YOLO tracking
    # --------------------------------------------------

    results = tracker.track(frame)


    # --------------------------------------------------
    # Draw RED line
    # --------------------------------------------------

    cv2.line(
        frame,
        (0, line_y_red),
        (frame_width, line_y_red),
        (0, 0, 255),
        3
    )

    cv2.putText(
        frame,
        "RED LINE",
        (10, line_y_red - 10),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 0, 255),
        2,
        cv2.LINE_AA
    )


    # --------------------------------------------------
    # Draw BLUE line
    # --------------------------------------------------

    cv2.line(
        frame,
        (0, line_y_blue),
        (frame_width, line_y_blue),
        (255, 0, 0),
        3
    )

    cv2.putText(
        frame,
        "BLUE LINE",
        (10, line_y_blue - 10),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 0, 0),
        2,
        cv2.LINE_AA
    )


    # --------------------------------------------------
    # Make sure detections exist
    # --------------------------------------------------

    if (
        results[0].boxes.data is not None
        and results[0].boxes.id is not None
    ):

        boxes = results[0].boxes.xyxy.cpu()

        track_ids = (
            results[0]
            .boxes
            .id
            .int()
            .cpu()
            .tolist()
        )

        class_indices = (
            results[0]
            .boxes
            .cls
            .int()
            .cpu()
            .tolist()
        )

        confidences = results[0].boxes.conf.cpu()


        # --------------------------------------------------
        # Process every detected object
        # --------------------------------------------------

        for box, track_id, class_idx, conf in zip(
            boxes,
            track_ids,
            class_indices,
            confidences
        ):

            x1, y1, x2, y2 = map(int, box)


            # --------------------------------------------------
            # Calculate center point
            # --------------------------------------------------

            cx = (x1 + x2) // 2
            cy = (y1 + y2) // 2


            # --------------------------------------------------
            # Get vehicle class
            # --------------------------------------------------

            class_name = class_list[class_idx]


            # --------------------------------------------------
            # Update vehicle counter
            # --------------------------------------------------

            counter.update(
                track_id,
                class_name,
                cy
            )


            # --------------------------------------------------
            # Draw center point
            # --------------------------------------------------

            cv2.circle(
                frame,
                (cx, cy),
                4,
                (0, 0, 255),
                -1
            )


            # --------------------------------------------------
            # Draw bounding box
            # --------------------------------------------------

            cv2.rectangle(
                frame,
                (x1, y1),
                (x2, y2),
                (0, 255, 0),
                2
            )


            # --------------------------------------------------
            # Display ID and class
            # --------------------------------------------------

            cv2.putText(
                frame,
                f"ID: {track_id} | {class_name}",
                (x1, max(y1 - 10, 20)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 255),
                2,
                cv2.LINE_AA
            )


    # --------------------------------------------------
    # Get current counts
    # --------------------------------------------------

    count_red_to_blue, count_blue_to_red = (
        counter.get_counts()
    )


    # --------------------------------------------------
    # Display DOWN counts
    # --------------------------------------------------

    y_offset = 30

    for class_name, count in count_red_to_blue.items():

        text = f"{class_name.upper()} DOWN: {count}"


        # Background box
        cv2.rectangle(
            frame,
            (5, y_offset - 25),
            (250, y_offset + 5),
            (0, 0, 0),
            -1
        )


        # White text
        cv2.putText(
            frame,
            text,
            (10, y_offset),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
            cv2.LINE_AA
        )

        y_offset += 35


    # --------------------------------------------------
    # Display UP counts
    # --------------------------------------------------

    y_offset += 20

    for class_name, count in count_blue_to_red.items():

        text = f"{class_name.upper()} UP: {count}"


        # Background box
        cv2.rectangle(
            frame,
            (5, y_offset - 25),
            (250, y_offset + 5),
            (0, 0, 0),
            -1
        )


        # White text
        cv2.putText(
            frame,
            text,
            (10, y_offset),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
            cv2.LINE_AA
        )

        y_offset += 35


    # --------------------------------------------------
    # Show video
    # --------------------------------------------------

    cv2.imshow(
        "YOLO Object Tracking & Counting",
        frame
    )


    # --------------------------------------------------
    # Press ESC to exit
    # --------------------------------------------------

    if cv2.waitKey(1) & 0xFF == 27:
        break


# --------------------------------------------------
# Release resources
# --------------------------------------------------

cap.release()

cv2.destroyAllWindows()