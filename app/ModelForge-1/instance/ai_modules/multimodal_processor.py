import os
import logging
import torch
import torchvision.transforms as transforms
from PIL import Image
import open_clip
from typing import Dict, List, Optional, Tuple, Any
import numpy as np
from dataclasses import dataclass
from enum import Enum

# Try to import BLIP-2
try:
    from lavis.models import load_model_and_preprocess
    BLIP2_AVAILABLE = True
except ImportError:
    BLIP2_AVAILABLE = False
    logging.warning("BLIP-2 not available. Install salesforce-lavis for BLIP-2 support.")

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModalityEngine(Enum):
    """Available multimodal engines"""
    CLIP = "clip"
    BLIP2 = "blip2"
    OPENAI = "openai"

@dataclass
class MultimodalConfig:
    """Configuration for multimodal processing"""
    engine: ModalityEngine = ModalityEngine.CLIP
    model_name: str = "ViT-B-32"
    pretrained: str = "openai"
    device: str = "cpu"
    max_tokens: int = 1000
    temperature: float = 0.7

class MultimodalProcessor:
    """Multimodal processor for text + image input"""
    
    def __init__(self, config: MultimodalConfig = None):
        self.config = config or MultimodalConfig()
        self.device = torch.device(self.config.device if torch.cuda.is_available() else "cpu")
        self.model = None
        self.tokenizer = None
        self.preprocess = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the multimodal model"""
        try:
            if self.config.engine == ModalityEngine.CLIP:
                self._initialize_clip()
            elif self.config.engine == ModalityEngine.BLIP2:
                self._initialize_blip2()
            else:
                raise ValueError(f"Unsupported engine: {self.config.engine}")
                
            logger.info(f"Initialized {self.config.engine.value} model on {self.device}")
        except Exception as e:
            logger.error(f"Failed to initialize model: {e}")
            raise
    
    def _initialize_clip(self):
        """Initialize CLIP model"""
        # Load CLIP model
        self.model, _, self.preprocess = open_clip.create_model_and_transforms(
            self.config.model_name, 
            pretrained=self.config.pretrained,
            device=self.device
        )
        self.tokenizer = open_clip.get_tokenizer(self.config.model_name)
        self.model.eval()
    
    def _initialize_blip2(self):
        """Initialize BLIP-2 model"""
        if not BLIP2_AVAILABLE:
            raise ImportError("BLIP-2 not available. Install salesforce-lavis for BLIP-2 support.")
        
        # Load BLIP-2 model
        self.model, self.preprocess, self.tokenizer = load_model_and_preprocess(
            "blip2_t5", "pretrain_flant5xl", device=self.device, is_eval=True
        )
        
        # Set up image preprocessing
        self.image_preprocess = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.48145466, 0.4578275, 0.40821073],
                               std=[0.26862954, 0.26130258, 0.27577711])
        ])
    
    def process_text_and_image(self, text: str, image_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Process text and optional image input to generate enhanced understanding
        
        Args:
            text: Text prompt
            image_path: Optional path to reference image
            
        Returns:
            Dictionary containing processed features and enhanced prompt
        """
        try:
            # Process text
            text_features = self._process_text(text)
            
            # Process image if provided
            image_features = None
            if image_path and os.path.exists(image_path):
                image_features = self._process_image(image_path)
            
            # Combine features
            combined_features = self._combine_features(text_features, image_features)
            
            # Generate enhanced prompt
            enhanced_prompt = self._generate_enhanced_prompt(text, text_features, image_features)
            
            return {
                'text_features': text_features,
                'image_features': image_features,
                'combined_features': combined_features,
                'enhanced_prompt': enhanced_prompt,
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Error processing text and image: {e}")
            return {
                'error': str(e),
                'success': False
            }
    
    def _process_text(self, text: str) -> torch.Tensor:
        """Process text input"""
        if self.config.engine == ModalityEngine.BLIP2:
            # BLIP-2 text processing
            with torch.no_grad():
                text_features = self.model.encode_text({"text_input": [text]})
                # BLIP-2 features are already normalized
        else:
            # CLIP text processing
            tokens = self.tokenizer([text]).to(self.device)
            with torch.no_grad():
                text_features = self.model.encode_text(tokens)
                text_features /= text_features.norm(dim=-1, keepdim=True)
        return text_features
    
    def _process_image(self, image_path: str) -> Optional[torch.Tensor]:
        """Process image input"""
        try:
            # Load and preprocess image
            image = Image.open(image_path).convert('RGB')
            
            if self.config.engine == ModalityEngine.BLIP2:
                # BLIP-2 preprocessing
                image_input = self.image_preprocess(image).unsqueeze(0).to(self.device)
            else:
                # CLIP preprocessing
                image_input = self.preprocess(image).unsqueeze(0).to(self.device)
            
            # Encode image
            with torch.no_grad():
                if self.config.engine == ModalityEngine.BLIP2:
                    # BLIP-2 encoding
                    image_features = self.model.encode_image(image_input)
                    # BLIP-2 features are already normalized
                else:
                    # CLIP encoding
                    image_features = self.model.encode_image(image_input)
                    image_features /= image_features.norm(dim=-1, keepdim=True)
            
            return image_features
        except Exception as e:
            logger.error(f"Error processing image {image_path}: {e}")
            return None
    
    def _combine_features(self, text_features: torch.Tensor, image_features: Optional[torch.Tensor]) -> Dict[str, Any]:
        """Combine text and image features"""
        combined = {
            'text_features': text_features.cpu().numpy() if text_features is not None else None,
            'image_features': image_features.cpu().numpy() if image_features is not None else None
        }
        
        # If we have both text and image features, compute similarity
        if text_features is not None and image_features is not None:
            similarity = (text_features @ image_features.T).cpu().numpy()
            combined['similarity'] = similarity.item()
        
        return combined
    
    def _generate_enhanced_prompt(self, original_text: str, text_features: torch.Tensor,
                                image_features: Optional[torch.Tensor]) -> str:
        """Generate enhanced prompt based on text and image features"""
        # For now, we'll just return the original text with some enhancement indicators
        # In a more advanced implementation, this could generate a more detailed prompt
        # based on image content analysis
        
        if image_features is not None:
            if self.config.engine == ModalityEngine.BLIP2:
                # For BLIP-2, we can generate a more detailed caption
                return f"{original_text} (enhanced with BLIP-2 image analysis)"
            else:
                return f"{original_text} (enhanced with image reference)"
        else:
            return original_text
    
    def get_image_description(self, image_path: str) -> str:
        """
        Generate a textual description of an image
        
        Args:
            image_path: Path to image file
            
        Returns:
            Textual description of the image
        """
        try:
            if self.config.engine == ModalityEngine.BLIP2:
                # Use BLIP-2 for image captioning
                raw_image = Image.open(image_path).convert("RGB")
                image_tensor = self.image_preprocess(raw_image).unsqueeze(0).to(self.device)
                
                # Generate caption
                caption = self.model.generate({"image": image_tensor})
                return caption[0]
            else:
                # This is a simplified implementation for CLIP
                # A more advanced implementation would use a model specifically trained for image captioning
                return "Image reference for 3D model generation"
        except Exception as e:
            logger.error(f"Error generating image description: {e}")
            return "Image reference"
    
    def compute_similarity(self, text: str, image_path: str) -> float:
        """
        Compute similarity between text and image
        
        Args:
            text: Text prompt
            image_path: Path to image file
            
        Returns:
            Similarity score between text and image
        """
        try:
            text_features = self._process_text(text)
            image_features = self._process_image(image_path)
            
            if text_features is not None and image_features is not None:
                similarity = (text_features @ image_features.T).cpu().numpy()
                return similarity.item()
            else:
                return 0.0
        except Exception as e:
            logger.error(f"Error computing similarity: {e}")
            return 0.0

# Convenience function for easy access
def create_multimodal_processor(config: MultimodalConfig = None) -> MultimodalProcessor:
    """Create and initialize a multimodal processor"""
    return MultimodalProcessor(config)