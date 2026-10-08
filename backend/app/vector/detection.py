import torch
from transformers import OwlViTProcessor, OwlViTForObjectDetection
from PIL import Image

class DetectionService:
    def __init__(self, model_name: str = "google/owlvit-base-patch32"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model_name = model_name
        self.processor = OwlViTProcessor.from_pretrained(self.model_name)
        self.model = OwlViTForObjectDetection.from_pretrained(self.model_name).to(self.device)

    def detect(self, image_path: str, text_prompts: list[str], threshold: float = 0.1) -> list[dict]:
        """
        Open-vocabulary object detection for a single image.
        """
        image = Image.open(image_path).convert("RGB")
        # Format prompts to improve OwlViT accuracy
        formatted_prompts = [f"a photo of a {p}" if not p.startswith("a photo of") else p for p in text_prompts]
        inputs = self.processor(text=[formatted_prompts], images=image, return_tensors="pt").to(self.device)
        
        with torch.no_grad():
            outputs = self.model(**inputs)
            
        target_sizes = torch.tensor([image.size[::-1]])
        results = self.processor.post_process_grounded_object_detection(outputs=outputs, target_sizes=target_sizes, threshold=threshold)
        
        detections = []
        boxes, scores, labels = results[0]["boxes"], results[0]["scores"], results[0]["labels"]
        
        for box, score, label in zip(boxes, scores, labels):
            detections.append({
                "label": text_prompts[label.item()],
                "confidence": score.item(),
                "bbox": {
                    "x1": float(box[0]),
                    "y1": float(box[1]),
                    "x2": float(box[2]),
                    "y2": float(box[3]),
                }
            })
        return detections

    def detect_batch(self, image_paths: list[str], text_prompts: list[str], threshold: float = 0.1) -> list[list[dict]]:
        """
        Batch processing for multiple images.
        """
        images = [Image.open(p).convert("RGB") for p in image_paths]
        formatted_prompts = [f"a photo of a {p}" if not p.startswith("a photo of") else p for p in text_prompts]
        
        inputs = self.processor(text=[formatted_prompts]*len(images), images=images, return_tensors="pt").to(self.device)
        with torch.no_grad():
            outputs = self.model(**inputs)
            
        target_sizes = torch.tensor([img.size[::-1] for img in images])
        results = self.processor.post_process_grounded_object_detection(outputs=outputs, target_sizes=target_sizes, threshold=threshold)
        
        batch_detections = []
        for i in range(len(images)):
            detections = []
            boxes, scores, labels = results[i]["boxes"], results[i]["scores"], results[i]["labels"]
            for box, score, label in zip(boxes, scores, labels):
                detections.append({
                    "label": text_prompts[label.item()],
                    "confidence": score.item(),
                    "bbox": {
                        "x1": float(box[0]),
                        "y1": float(box[1]),
                        "x2": float(box[2]),
                        "y2": float(box[3]),
                    }
                })
            batch_detections.append(detections)
        return batch_detections

    def detect_with_query(self, image_path: str, query: str, threshold: float = 0.1) -> list[dict]:
        """
        Derives visual concepts from a natural language query and detects them.
        Example: "Did a person carrying a large umbrella enter?" -> ["person", "umbrella", "person carrying umbrella"]
        """
        # Basic heuristic extraction for fallback, or we can assume the LLM parser fed us concepts.
        # For this method, we'll try detecting the whole query and some derived parts.
        concepts = [query]
        # Basic extraction 
        for entity in ["person", "car", "truck", "bag", "umbrella", "bicycle"]:
            if entity in query.lower():
                concepts.append(entity)
                
        return self.detect(image_path, list(set(concepts)), threshold)


_detection_service = None

def get_detection_service() -> DetectionService:
    """Loads OwlViT once per process instead of on every request."""
    global _detection_service
    if _detection_service is None:
        _detection_service = DetectionService()
    return _detection_service
