from ultralytics import YOLO


class VehicleTracker:

    def __init__(self, model_path="computer_vision/models/yolo11s.pt"):
        """
        Load YOLO model for object tracking.
        """

        self.model = YOLO(model_path)

        # YOLO class names
        self.class_names = self.model.names

    def track(self, frame):
        """
        Track vehicles in the given frame.
        """

        results = self.model.track(
            frame,
            persist=True,
            verbose=False
        )

        return results