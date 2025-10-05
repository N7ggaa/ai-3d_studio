"""
Enhanced AI Generation Module with YouTube Reference Support
Implements advanced features for better Roblox-optimized model generation
"""

import os
import json
import hashlib
import logging
import requests
import subprocess
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import trimesh
from pathlib import Path
import cv2
import yt_dlp

logger = logging.getLogger(__name__)

class AssetType(Enum):
    SINGLE_OBJECT = "single_object"
    PROP_PACK = "prop_pack"
    ENVIRONMENT = "environment"
    CHARACTER = "character"
    VEHICLE = "vehicle"
    WORLD = "world"

class StyleFilter(Enum):
    REALISTIC = "realistic"
    ROBLOX_CARTOONY = "roblox_cartoony"
    VOXEL = "voxel"
    ANIME = "anime"
    LOW_POLY = "low_poly"

class PerformancePreset(Enum):
    MOBILE_FRIENDLY = "mobile"  # <3k tris
    BALANCED = "balanced"       # 3-10k tris
    HIGH_DETAIL = "high"        # 10-50k tris
    CINEMATIC = "cinematic"     # 50k+ tris

@dataclass
class GenerationConfig:
    """Enhanced generation configuration"""
    prompt: str
    youtube_urls: List[str] = None
    reference_images: List[str] = None
    asset_type: AssetType = AssetType.SINGLE_OBJECT
    style: StyleFilter = StyleFilter.ROBLOX_CARTOONY
    performance: PerformancePreset = PerformancePreset.BALANCED
    generate_lods: bool = True
    lod_levels: int = 3
    generate_variations: bool = False
    variation_count: int = 5
    auto_rig: bool = False
    auto_texture: bool = True
    texture_resolution: int = 1024
    use_roblox_materials: bool = True
    poly_budget: Optional[int] = None
    
    def get_poly_budget(self) -> int:
        """Get polygon budget based on performance preset"""
        if self.poly_budget:
            return self.poly_budget
            
        budgets = {
            PerformancePreset.MOBILE_FRIENDLY: {
                AssetType.SINGLE_OBJECT: 1500,
                AssetType.PROP_PACK: 5000,
                AssetType.ENVIRONMENT: 15000,
                AssetType.CHARACTER: 3000,
                AssetType.VEHICLE: 5000,
                AssetType.WORLD: 50000
            },
            PerformancePreset.BALANCED: {
                AssetType.SINGLE_OBJECT: 5000,
                AssetType.PROP_PACK: 15000,
                AssetType.ENVIRONMENT: 50000,
                AssetType.CHARACTER: 10000,
                AssetType.VEHICLE: 15000,
                AssetType.WORLD: 150000
            },
            PerformancePreset.HIGH_DETAIL: {
                AssetType.SINGLE_OBJECT: 15000,
                AssetType.PROP_PACK: 50000,
                AssetType.ENVIRONMENT: 150000,
                AssetType.CHARACTER: 30000,
                AssetType.VEHICLE: 40000,
                AssetType.WORLD: 500000
            },
            PerformancePreset.CINEMATIC: {
                AssetType.SINGLE_OBJECT: 50000,
                AssetType.PROP_PACK: 150000,
                AssetType.ENVIRONMENT: 500000,
                AssetType.CHARACTER: 100000,
                AssetType.VEHICLE: 100000,
                AssetType.WORLD: 1500000
            }
        }
        
        return budgets[self.performance][self.asset_type]

class YouTubeProcessor:
    """Extract frames and depth information from YouTube videos"""
    
    def __init__(self, cache_dir: str = "cache/youtube_frames"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
    def extract_frames(self, url: str, max_frames: int = 30) -> List[np.ndarray]:
        """Extract key frames from YouTube video"""
        video_id = self._get_video_id(url)
        cache_path = self.cache_dir / f"{video_id}"
        
        if cache_path.exists():
            # Load from cache
            frames = []
            for img_path in sorted(cache_path.glob("*.jpg"))[:max_frames]:
                frame = cv2.imread(str(img_path))
                frames.append(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            return frames
            
        # Download and extract
        cache_path.mkdir(exist_ok=True)
        
        ydl_opts = {
            'format': 'best[height<=720]',
            'quiet': True,
            'no_warnings': True,
            'outtmpl': str(cache_path / 'video.%(ext)s')
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                video_path = cache_path / f"video.{info['ext']}"
        except Exception as e:
            logger.error(f"Failed to download YouTube video: {e}")
            return []
            
        # Extract frames
        frames = self._extract_keyframes(video_path, cache_path, max_frames)
        
        # Clean up video file
        video_path.unlink()
        
        return frames
        
    def _get_video_id(self, url: str) -> str:
        """Extract video ID from YouTube URL"""
        import re
        patterns = [
            r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
            r'(?:embed\/)([0-9A-Za-z_-]{11})',
            r'(?:watch\?v=)([0-9A-Za-z_-]{11})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        # Fallback to URL hash
        return hashlib.md5(url.encode()).hexdigest()[:11]
        
    def _extract_keyframes(self, video_path: Path, output_dir: Path, max_frames: int) -> List[np.ndarray]:
        """Extract keyframes using scene detection"""
        cap = cv2.VideoCapture(str(video_path))
        frames = []
        frame_count = 0
        
        # Simple uniform sampling for now
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        sample_rate = max(1, total_frames // max_frames)
        
        while cap.isOpened() and len(frames) < max_frames:
            ret, frame = cap.read()
            if not ret:
                break
                
            if frame_count % sample_rate == 0:
                # Save frame
                frame_path = output_dir / f"frame_{frame_count:06d}.jpg"
                cv2.imwrite(str(frame_path), frame)
                frames.append(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                
            frame_count += 1
            
        cap.release()
        return frames

class PromptEnhancer:
    """Enhance prompts with style and optimization constraints"""
    
    def enhance(self, prompt: str, config: GenerationConfig) -> str:
        """Enhance prompt with style and technical constraints"""
        
        # Base enhancements
        enhanced = prompt
        
        # Add style modifiers
        style_modifiers = {
            StyleFilter.REALISTIC: "photorealistic, high detail, PBR materials",
            StyleFilter.ROBLOX_CARTOONY: "stylized cartoon, smooth surfaces, bright colors, Roblox style",
            StyleFilter.VOXEL: "voxel art, cubic shapes, minecraft style, blocky",
            StyleFilter.ANIME: "anime style, cel shaded, vibrant colors",
            StyleFilter.LOW_POLY: "low poly, flat shaded, geometric, minimal detail"
        }
        
        enhanced += f", {style_modifiers[config.style]}"
        
        # Add performance constraints
        poly_budget = config.get_poly_budget()
        enhanced += f", optimized for games, maximum {poly_budget} polygons"
        
        # Add Roblox-specific constraints
        enhanced += ", exterior only, no interior details, simple clean geometry"
        enhanced += ", suitable for Roblox, game asset, no unnecessary complexity"
        
        # Add asset type specifics
        if config.asset_type == AssetType.SINGLE_OBJECT:
            enhanced += ", single isolated object, centered, no background"
        elif config.asset_type == AssetType.PROP_PACK:
            enhanced += ", collection of related props, modular pieces"
        elif config.asset_type == AssetType.ENVIRONMENT:
            enhanced += ", complete environment, room scale, architectural"
        elif config.asset_type == AssetType.CHARACTER:
            enhanced += ", character model, T-pose, symmetrical, riggable"
        elif config.asset_type == AssetType.VEHICLE:
            enhanced += ", vehicle, separate wheels, functional parts"
        elif config.asset_type == AssetType.WORLD:
            enhanced += ", large scale world, terrain, multiple areas"
            
        return enhanced

class LODGenerator:
    """Generate multiple LOD levels for models"""
    
    def generate_lods(self, mesh: trimesh.Trimesh, levels: int = 3) -> List[trimesh.Trimesh]:
        """Generate LOD levels with progressive decimation"""
        lods = [mesh.copy()]  # LOD0 is original
        
        # Calculate decimation ratios
        ratios = np.linspace(0.5, 0.1, levels - 1)
        
        for ratio in ratios:
            target_faces = int(len(mesh.faces) * ratio)
            if target_faces < 10:
                target_faces = 10
                
            try:
                # Use quadric decimation for better quality
                simplified = mesh.simplify_quadric_decimation(target_faces)
                lods.append(simplified)
            except:
                # Fallback to basic simplification
                simplified = mesh.simplify_quadric(target_faces)
                lods.append(simplified)
                
        return lods
        
    def calculate_lod_distances(self, mesh: trimesh.Trimesh) -> List[float]:
        """Calculate appropriate LOD switching distances"""
        # Based on bounding box size
        bounds = mesh.bounds
        size = np.linalg.norm(bounds[1] - bounds[0])
        
        # LOD distances as multipliers of object size
        distances = [
            0,        # LOD0: close range
            size * 5,  # LOD1: medium range
            size * 15, # LOD2: far range
            size * 50  # LOD3: very far
        ]
        
        return distances

class VariationGenerator:
    """Generate variations of models"""
    
    def generate_variations(self, base_mesh: trimesh.Trimesh, count: int = 5) -> List[trimesh.Trimesh]:
        """Generate variations with different parameters"""
        variations = []
        
        for i in range(count):
            variant = base_mesh.copy()
            
            # Random scale variation (0.8x to 1.2x)
            scale = np.random.uniform(0.8, 1.2, 3)
            variant.apply_scale(scale)
            
            # Slight rotation for variety
            angle = np.random.uniform(-15, 15)
            rotation = trimesh.transformations.rotation_matrix(
                np.radians(angle), [0, 1, 0]
            )
            variant.apply_transform(rotation)
            
            # Add noise for organic variation (small amount)
            if i % 2 == 0:
                noise = np.random.normal(0, 0.01, variant.vertices.shape)
                variant.vertices += noise
                
            variations.append(variant)
            
        return variations

class EnhancedModelGenerator:
    """Main enhanced generation pipeline"""
    
    def __init__(self, output_dir: str = "generated/enhanced"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.youtube_processor = YouTubeProcessor()
        self.prompt_enhancer = PromptEnhancer()
        self.lod_generator = LODGenerator()
        self.variation_generator = VariationGenerator()
        
    def generate(self, config: GenerationConfig) -> Dict[str, Any]:
        """Generate models with all enhanced features"""
        
        # Extract YouTube frames if provided
        reference_data = {}
        if config.youtube_urls:
            logger.info(f"Extracting frames from {len(config.youtube_urls)} YouTube videos")
            all_frames = []
            for url in config.youtube_urls:
                frames = self.youtube_processor.extract_frames(url)
                all_frames.extend(frames)
            reference_data['frames'] = all_frames
            
        # Enhance prompt
        enhanced_prompt = self.prompt_enhancer.enhance(config.prompt, config)
        logger.info(f"Enhanced prompt: {enhanced_prompt}")
        
        # Generate base model (simplified for example)
        base_mesh = self._generate_base_model(enhanced_prompt, reference_data, config)
        
        # Generate LODs
        lods = []
        if config.generate_lods:
            logger.info(f"Generating {config.lod_levels} LOD levels")
            lods = self.lod_generator.generate_lods(base_mesh, config.lod_levels)
            
        # Generate variations
        variations = []
        if config.generate_variations:
            logger.info(f"Generating {config.variation_count} variations")
            variations = self.variation_generator.generate_variations(base_mesh, config.variation_count)
            
        # Save all outputs
        output_data = self._save_outputs(base_mesh, lods, variations, config)
        
        return {
            'success': True,
            'base_model': output_data['base'],
            'lods': output_data.get('lods', []),
            'variations': output_data.get('variations', []),
            'config': config.__dict__,
            'enhanced_prompt': enhanced_prompt
        }
        
    def _generate_base_model(self, prompt: str, reference_data: Dict, config: GenerationConfig) -> trimesh.Trimesh:
        """Generate the base model (placeholder implementation)"""
        # This would integrate with your existing AI generation
        # For now, create a simple procedural model as example
        
        if config.asset_type == AssetType.SINGLE_OBJECT:
            # Simple box as placeholder
            mesh = trimesh.creation.box(extents=[1, 1, 1])
        elif config.asset_type == AssetType.CHARACTER:
            # Simple capsule for character
            mesh = trimesh.creation.capsule(height=2, radius=0.5)
        else:
            # Default sphere
            mesh = trimesh.creation.icosphere(subdivisions=2, radius=1)
            
        # Apply poly budget
        target_faces = config.get_poly_budget() // 2
        if len(mesh.faces) > target_faces:
            mesh = mesh.simplify_quadric_decimation(target_faces)
            
        return mesh
        
    def _save_outputs(self, base_mesh: trimesh.Trimesh, lods: List, variations: List, config: GenerationConfig) -> Dict:
        """Save all generated outputs"""
        timestamp = hashlib.md5(config.prompt.encode()).hexdigest()[:8]
        base_name = f"{config.asset_type.value}_{timestamp}"
        
        output_data = {}
        
        # Save base model
        base_path = self.output_dir / f"{base_name}.obj"
        base_mesh.export(base_path)
        output_data['base'] = str(base_path)
        
        # Save LODs
        if lods:
            lod_paths = []
            for i, lod in enumerate(lods):
                lod_path = self.output_dir / f"{base_name}_LOD{i}.obj"
                lod.export(lod_path)
                lod_paths.append(str(lod_path))
            output_data['lods'] = lod_paths
            
        # Save variations
        if variations:
            var_paths = []
            for i, var in enumerate(variations):
                var_path = self.output_dir / f"{base_name}_var{i}.obj"
                var.export(var_path)
                var_paths.append(str(var_path))
            output_data['variations'] = var_paths
            
        # Save metadata
        metadata = {
            'config': config.__dict__,
            'paths': output_data,
            'stats': {
                'base_faces': len(base_mesh.faces),
                'base_vertices': len(base_mesh.vertices),
                'lod_count': len(lods),
                'variation_count': len(variations)
            }
        }
        
        metadata_path = self.output_dir / f"{base_name}_metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2, default=str)
            
        return output_data

# Example usage
if __name__ == "__main__":
    # Configure generation
    config = GenerationConfig(
        prompt="Medieval tavern table with mugs and plates",
        youtube_urls=["https://youtube.com/watch?v=example"],
        asset_type=AssetType.PROP_PACK,
        style=StyleFilter.ROBLOX_CARTOONY,
        performance=PerformancePreset.BALANCED,
        generate_lods=True,
        generate_variations=True,
        variation_count=3
    )
    
    # Generate
    generator = EnhancedModelGenerator()
    result = generator.generate(config)
    
    print(f"Generation complete: {result}")
