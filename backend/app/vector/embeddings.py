import torch
from transformers import CLIPProcessor, CLIPModel
from PIL import Image
import numpy as np

class EmbeddingService:
    def __init__(self, model_name: str = "openai/clip-vit-base-patch32"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model_name = model_name
        
        # Load the multimodal model (CLIP) which supports shared image/text embedding spaces
        self.model = CLIPModel.from_pretrained(self.model_name).to(self.device)
        self.processor = CLIPProcessor.from_pretrained(self.model_name)
        self.vector_dimension = self.model.config.projection_dim

    def encode_text(self, text: str) -> list[float]:
        inputs = self.processor(text=[text], return_tensors="pt", padding=True).to(self.device)
        with torch.no_grad():
            text_features = self.model.get_text_features(**inputs)
            if not isinstance(text_features, torch.Tensor):
                text_features = getattr(text_features, 'text_embeds', text_features[0])
            # Normalize the vector for cosine similarity
            text_features = text_features / text_features.norm(p=2, dim=-1, keepdim=True)
            
        return text_features.cpu().numpy()[0].tolist()

    def encode_image(self, image_path: str) -> list[float]:
        image = Image.open(image_path).convert("RGB")
        inputs = self.processor(images=image, return_tensors="pt").to(self.device)
        with torch.no_grad():
            image_features = self.model.get_image_features(**inputs)
            if not isinstance(image_features, torch.Tensor):
                image_features = getattr(image_features, 'image_embeds', getattr(image_features, 'pooler_output', image_features[0]))
            # Normalize
            image_features = image_features / image_features.norm(p=2, dim=-1, keepdim=True)
            
        return image_features.cpu().numpy()[0].tolist()

    def encode_images(self, image_paths: list[str]) -> list[list[float]]:
        images = [Image.open(p).convert("RGB") for p in image_paths]
        inputs = self.processor(images=images, return_tensors="pt").to(self.device)
        with torch.no_grad():
            image_features = self.model.get_image_features(**inputs)
            if not isinstance(image_features, torch.Tensor):
                image_features = getattr(image_features, 'image_embeds', getattr(image_features, 'pooler_output', image_features[0]))
            image_features = image_features / image_features.norm(p=2, dim=-1, keepdim=True)
            
        return image_features.cpu().numpy().tolist()

# Note: In a production celery worker with multiple processes, 
# it's often better to initialize the model per-worker-process 
# rather than as a global singleton at import time.

embedding_service = EmbeddingService()
