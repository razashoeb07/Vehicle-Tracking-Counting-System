from ultralytics import YOLO


class VehicleDetector:
    def __init__(self, model_path="computer_vision/models/yolo11n.pt"):
        """
        Load YOLO model
        """
        self.model = YOLO(model_path)
        self.class_names = self.model.names

    def track_objects(self, frame):
        """
        Run tracking on a frame
        """
        results = self.model.track(
            frame,
            persist=True,
            conf=0.40,
            iou=0.5,
            verbose=False
        )

        return results

    def get_class_name(self, class_id):
        """
        Return class name from class ID
        """
        return self.class_names[class_id]