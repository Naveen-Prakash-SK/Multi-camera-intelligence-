from abc import ABC, abstractmethod
import cv2
from typing import Iterator, Tuple, Optional
import numpy as np

class FrameSource(ABC):
    """
    Abstract interface for frame ingestion.
    Allows downstream intelligence (Detection, Tracking, Embedding) 
    to be perfectly agnostic to whether footage is live or recorded.
    """
    
    @abstractmethod
    def get_frames(self) -> Iterator[Tuple[int, float, np.ndarray]]:
        """
        Yields (frame_count, timestamp_s, frame_bgr)
        """
        pass
        
    @abstractmethod
    def close(self):
        pass

class RecordedVideoSource(FrameSource):
    def __init__(self, file_path: str, fps_sample_rate: float = 1.0):
        self.file_path = file_path
        self.fps_sample_rate = fps_sample_rate
        self.cap = cv2.VideoCapture(file_path)
        if not self.cap.isOpened():
            raise ValueError(f"Could not open video file: {file_path}")
            
        self.source_fps = self.cap.get(cv2.CAP_PROP_FPS)
        if self.source_fps <= 0:
            self.source_fps = 30.0
            
        self.frame_interval = max(1, int(self.source_fps / self.fps_sample_rate))
        
    def get_frames(self) -> Iterator[Tuple[int, float, np.ndarray]]:
        frame_count = 0
        while self.cap.isOpened():
            ret, frame = self.cap.read()
            if not ret:
                break
                
            if frame_count % self.frame_interval == 0:
                timestamp_s = frame_count / self.source_fps
                yield frame_count, timestamp_s, frame
                
            frame_count += 1
            
    def close(self):
        if self.cap.isOpened():
            self.cap.release()

class LiveStreamBuffer(FrameSource):
    """
    Conceptual architecture for future live streaming.
    DO NOT wire up to external APIs yet.
    """
    def __init__(self, stream_url: str, max_buffer_size: int = 30):
        self.stream_url = stream_url
        self.max_buffer_size = max_buffer_size
        # internal queue logic here
        
    def get_frames(self) -> Iterator[Tuple[int, float, np.ndarray]]:
        # Poll internal queue, yielding latest frames, dropping if behind
        pass
        
    def close(self):
        pass
