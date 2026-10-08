import torch
import open_clip
from PIL import Image
import numpy as np

class EmbeddingService:
    def __init__(self, model_name: str = "ViT-B-16-SigLIP", pretrained: str = "webli"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model_name = model_name
        
        print(f"Loading SigLIP model for text embeddings: {model_name}")
        self.model, _, self.preprocess = open_clip.create_model_and_transforms(self.model_name, pretrained=pretrained)
        self.model = self.model.to(self.device)
        self.model.eval()
        self.tokenizer = open_clip.get_tokenizer(self.model_name)
        self.vector_dimension = 768

    def encode_text(self, text: str) -> list[float]:
        text_tokens = self.tokenizer([text]).to(self.device)
        with torch.no_grad():
            text_features = self.model.encode_text(text_tokens)
            text_features = text_features / text_features.norm(p=2, dim=-1, keepdim=True)
            
        return text_features.cpu().numpy()[0].tolist()

    def encode_image(self, image_path: str) -> list[float]:
        image = Image.open(image_path).convert("RGB")
        image_input = self.preprocess(image).unsqueeze(0).to(self.device)
        with torch.no_grad():
            image_features = self.model.encode_image(image_input)
            image_features = image_features / image_features.norm(p=2, dim=-1, keepdim=True)
            
        return image_features.cpu().numpy()[0].tolist()

    def encode_images(self, image_paths: list[str]) -> list[list[float]]:
        images = [Image.open(p).convert("RGB") for p in image_paths]
        inputs = torch.cat([self.preprocess(img).unsqueeze(0) for img in images]).to(self.device)
        with torch.no_grad():
            image_features = self.model.encode_image(inputs)
            image_features = image_features / image_features.norm(p=2, dim=-1, keepdim=True)
            
        return image_features.cpu().numpy().tolist()
