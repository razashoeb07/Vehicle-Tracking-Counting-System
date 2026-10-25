
import threading
import time
import cv2


class LiveState:
    def __init__(self):
        self.lock = threading.Lock()
        self.status = "idle"
        self.frame_jpeg = None
        self.counts = {"down": {}, "up": {}}
        self.progress = 0
        self.error = None
        self.started_at = None
        self.updated_at = None

    def start(self):
        with self.lock:
            self.status = "processing"
            self.frame_jpeg = None
            self.counts = {"down": {}, "up": {}}
            self.progress = 0
            self.error = None
            self.started_at = time.time()
            self.updated_at = self.started_at

    def update_frame(self, frame, counts):
        success, encoded = cv2.imencode(
            ".jpg", frame,
            [int(cv2.IMWRITE_JPEG_QUALITY), 75]
        )

        if not success:
            return

        with self.lock:
            self.frame_jpeg = encoded.tobytes()
            self.counts = counts
            self.updated_at = time.time()

    def finish(self, status="completed", error=None):
        with self.lock:
            self.status = status
            self.error = error
            self.updated_at = time.time()

    def snapshot(self):
        with self.lock:
            return {
                "status": self.status,
                "frame_jpeg": self.frame_jpeg,
                "counts": self.counts,
                "progress": self.progress,
                "error": self.error,
                "updated_at": self.updated_at,
            }


live_state = LiveState()
