from typing import Optional, Tuple
from threading import Thread
import queue
import cv2
import numpy as np

class CameraInterface:
    """Controls drone cameras and processes image streams."""
    
    def __init__(self, camera_id: int = 0):
        self.camera_id = camera_id
        self.cap = None
        self.frame_queue = queue.Queue(maxsize=10)
        self._streaming = False
        self._stream_thread = None
        
    def initialize(self) -> bool:
        """Initialize camera connection."""
        try:
            self.cap = cv2.VideoCapture(self.camera_id)
            if not self.cap.isOpened():
                return False
            
            # Set camera properties
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            
            return True
        except Exception as e:
            print(f"Camera initialization error: {e}")
            return False
            
    def capture_frame(self) -> Optional[np.ndarray]:
        """Capture a single frame from the camera."""
        if not self.cap or not self.cap.isOpened():
            return None
            
        ret, frame = self.cap.read()
        if ret:
            return frame
        return None
        
    def start_stream(self):
        """Start continuous frame capture in a separate thread."""
        if self._streaming:
            return
            
        self._streaming = True
        self._stream_thread = Thread(target=self._stream_worker)
        self._stream_thread.start()
        
    def stop_stream(self):
        """Stop continuous frame capture."""
        self._streaming = False
        if self._stream_thread:
            self._stream_thread.join()
            
    def get_latest_frame(self) -> Optional[np.ndarray]:
        """Get the latest frame from the stream."""
        try:
            return self.frame_queue.get_nowait()
        except queue.Empty:
            return None
            
    def _stream_worker(self):
        """Worker thread for continuous frame capture."""
        while self._streaming:
            frame = self.capture_frame()
            if frame is not None:
                try:
                    self.frame_queue.put_nowait(frame)
                except queue.Full:
                    # Remove oldest frame and add new one
                    try:
                        self.frame_queue.get_nowait()
                        self.frame_queue.put_nowait(frame)
                    except queue.Empty:
                        pass
                        
    def detect_objects(self, frame: np.ndarray, confidence_threshold: float = 0.5) -> list:
        """Simple object detection using OpenCV (placeholder for more advanced detection)."""
        # Convert to grayscale for simple edge detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Edge detection
        edges = cv2.Canny(blurred, 50, 150)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        objects = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 100:  # Filter small contours
                x, y, w, h = cv2.boundingRect(contour)
                objects.append({
                    'bbox': (x, y, w, h),
                    'area': area,
                    'confidence': min(area / 10000, 1.0)  # Crude confidence score
                })
                
        return objects
        
    def calculate_optical_flow(self, prev_frame: np.ndarray, curr_frame: np.ndarray) -> np.ndarray:
        """Calculate optical flow between two frames."""
        prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
        curr_gray = cv2.cvtColor(curr_frame, cv2.COLOR_BGR2GRAY)
        
        flow = cv2.calcOpticalFlowPyrLK(prev_gray, curr_gray, None, None)
        return flow
        
    def close(self):
        """Close camera connection."""
        self.stop_stream()
        if self.cap:
            self.cap.release()