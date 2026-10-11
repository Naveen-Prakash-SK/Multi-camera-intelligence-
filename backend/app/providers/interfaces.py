from abc import ABC, abstractmethod
from typing import List, Dict, Any
import numpy as np

class TextEmbeddingProvider(ABC):
    @abstractmethod
    def embed_text(self, text: str) -> np.ndarray:
        pass

class ImageEmbeddingProvider(ABC):
    @abstractmethod
    def embed_image(self, image_data: bytes) -> np.ndarray:
        pass

class DetectionProvider(ABC):
    @abstractmethod
    def detect(self, image_data: bytes) -> List[Dict[str, Any]]:
        pass

class TrackingProvider(ABC):
    @abstractmethod
    def track(self, detections: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        pass

class PersonReIDProvider(ABC):
    @abstractmethod
    def extract_features(self, image_data: bytes) -> np.ndarray:
        pass

class VehicleReIDProvider(ABC):
    @abstractmethod
    def extract_features(self, image_data: bytes) -> np.ndarray:
        pass

class ReasoningProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str) -> str:
        pass

class VisionLanguageProvider(ABC):
    @abstractmethod
    def analyze(self, image_data: bytes, prompt: str) -> str:
        pass
