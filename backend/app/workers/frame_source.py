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

class FFmpegVideoSource(FrameSource):
    """
    Video preprocessing pipeline using FFmpeg and OpenCV.
    Uses FFmpeg to decode, scale, and sample frames, piping directly to OpenCV as raw bytes.
    This is significantly faster and more robust than cv2.VideoCapture for large files.
    """
    def __init__(self, file_path: str, fps_sample_rate: float = 1.0, width: int = 1280, height: int = 720):
        import subprocess
        self.file_path = file_path
        self.fps = fps_sample_rate
        self.width = width
        self.height = height
        
        # FFmpeg command to read video, scale it, set fps, and output raw BGR24 frames to stdout
        command = [
            'ffmpeg',
            '-y',
            '-i', self.file_path,
            '-vf', f'scale={self.width}:{self.height},fps={self.fps}',
            '-f', 'image2pipe',
            '-pix_fmt', 'bgr24',
            '-vcodec', 'rawvideo',
            '-'
        ]
        
        self.process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, bufsize=10**8)
        self.frame_size = self.width * self.height * 3
        
    def get_frames(self) -> Iterator[Tuple[int, float, np.ndarray]]:
        frame_count = 0
        while True:
            raw_frame = self.process.stdout.read(self.frame_size)
            if len(raw_frame) != self.frame_size:
                break
                
            frame = np.frombuffer(raw_frame, np.uint8).reshape((self.height, self.width, 3))
            timestamp_s = frame_count / self.fps
            yield frame_count, timestamp_s, frame
            frame_count += 1
            
    def close(self):
        if self.process:
            self.process.terminate()
            self.process.wait()

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
