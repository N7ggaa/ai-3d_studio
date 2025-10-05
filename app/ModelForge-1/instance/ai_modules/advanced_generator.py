#!/usr/bin/env python3
"""
Advanced AI-Powered 3D Model Generator
Multiple generation engines with sophisticated capabilities
"""

import os
import logging
import numpy as np
import trimesh
import json
import requests
import time
import random
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
import math

# Import geometry generator
from instance.ai_modules.geometry_generator import create_geometry_generator, GeometryConfig, GeometryEngine

# Import texture generator
from instance.ai_modules.texture_generator import create_texture_generator, TextureConfig, TextureEngine

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GenerationEngine(Enum):
    """Available generation engines"""
    PROCEDURAL = "procedural"
    AI_ENHANCED = "ai_enhanced"
    HYBRID = "hybrid"
    TEXTURE_GENERATED = "texture_generated"

@dataclass
class GenerationConfig:
    """Configuration for model generation"""
    engine: GenerationEngine
    complexity: int = 5  # 1-10 scale
    detail_level: int = 7  # 1-10 scale
    material_style: str = "realistic"
    generate_textures: bool = True
    generate_materials: bool = True
    variations: int = 1
    seed: Optional[int] = None

class AdvancedModelGenerator:
    """Advanced AI-powered 3D model generator"""
    
    def __init__(self):
        self.engines = {
            GenerationEngine.PROCEDURAL: self._procedural_generation,
            GenerationEngine.AI_ENHANCED: self._ai_enhanced_generation,
            GenerationEngine.HYBRID: self._hybrid_generation,
            GenerationEngine.TEXTURE_GENERATED: self._texture_generated_generation
        }
        
        # Initialize geometry generator
        self.geometry_generator = create_geometry_generator()
        
        # Initialize texture generator
        self.texture_generator = create_texture_generator()
        
        # Initialize random seed
        if not hasattr(self, '_seed_initialized'):
            random.seed(time.time())
            np.random.seed(int(time.time()))
            self._seed_initialized = True
    
    def generate_model(self, prompt: str, config: GenerationConfig, reference_image_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a 3D model using the specified engine
        
        Args:
            prompt: Text description of the model
            config: Generation configuration
            reference_image_path: Optional reference image
            
        Returns:
            Dict containing model data and metadata
        """
        logger.info(f"Generating model with {config.engine.value} engine")
        
        # Set seed if provided
        if config.seed is not None:
            random.seed(config.seed)
            np.random.seed(config.seed)
        
        # Get the appropriate generation function
        generator_func = self.engines.get(config.engine)
        if not generator_func:
            raise ValueError(f"Unknown generation engine: {config.engine}")
        
        # Generate the model
        mesh = generator_func(prompt, config, reference_image_path)
        
        # Generate textures and materials if requested
        textures = {}
        materials = {}
        
        if config.generate_textures:
            textures = self._generate_textures(prompt, config)
        
        if config.generate_materials:
            materials = self._generate_materials(prompt, config)
        
        # Generate metadata
        metadata = self._generate_metadata(prompt, config, mesh)
        
        return {
            'mesh': mesh,
            'textures': textures,
            'materials': materials,
            'metadata': metadata,
            'config': config
        }
    
    def _procedural_generation(self, prompt: str, config: GenerationConfig, reference_image_path: Optional[str] = None) -> trimesh.Trimesh:
        """Advanced procedural generation with complex shapes"""
        # IMPORTANT: Add constraints to prevent interior geometry
        prompt_lower = prompt.lower()
        prompt_enhanced = prompt + " exterior only, no interior details, simple clean geometry, low poly game asset"
        
        # Try to generate geometry using the new geometry generator
        try:
            # Pass enhanced prompt to enforce simplicity
            geometry_result = self.geometry_generator.generate_geometry(prompt_enhanced, reference_image_path)
            if geometry_result['success']:
                # Convert numpy arrays to trimesh
                vertices = geometry_result['vertices']
                faces = geometry_result['faces']
                mesh = trimesh.Trimesh(vertices=vertices, faces=faces)
                return mesh
        except Exception as e:
            logger.warning(f"Geometry generator failed, falling back to traditional procedural generation: {e}")
        
        # Analyze prompt for shape characteristics
        shape_info = self._analyze_prompt(prompt)
        
        # Generate base shape
        base_mesh = self._generate_base_shape(shape_info, config)
        
        # Add details based on complexity
        detailed_mesh = self._add_details(base_mesh, shape_info, config)
        
        # Apply transformations
        final_mesh = self._apply_transformations(detailed_mesh, shape_info, config)
        
        return final_mesh
    
    def _ai_enhanced_generation(self, prompt: str, config: GenerationConfig, reference_image_path: Optional[str] = None) -> trimesh.Trimesh:
        """AI-enhanced generation using external APIs"""
        try:
            # Try to use external AI service (if configured)
            if self._has_ai_api_access():
                return self._call_external_ai_api(prompt, config, reference_image_path)
        except Exception as e:
            logger.warning(f"AI API failed, falling back to procedural: {e}")
        
        # Fallback to enhanced procedural generation
        return self._enhanced_procedural_generation(prompt, config, reference_image_path)
    
    def _hybrid_generation(self, prompt: str, config: GenerationConfig, reference_image_path: Optional[str] = None) -> trimesh.Trimesh:
        """Hybrid approach combining multiple generation methods"""
        # Generate multiple variations
        meshes = []
        
        # Procedural base
        proc_mesh = self._procedural_generation(prompt, config, reference_image_path)
        meshes.append(proc_mesh)
        
        # Enhanced procedural
        enh_mesh = self._enhanced_procedural_generation(prompt, config, reference_image_path)
        meshes.append(enh_mesh)
        
        # Try AI if available
        try:
            ai_mesh = self._ai_enhanced_generation(prompt, config, reference_image_path)
            meshes.append(ai_mesh)
        except:
            pass
        
        # Combine or select best mesh
        if len(meshes) > 1:
            return self._select_best_mesh(meshes, prompt, config)
        else:
            return meshes[0]
    
    def _texture_generated_generation(self, prompt: str, config: GenerationConfig, reference_image_path: Optional[str] = None) -> trimesh.Trimesh:
        """Generation with focus on texture and material quality"""
        # Generate base mesh
        base_mesh = self._procedural_generation(prompt, config, reference_image_path)
        
        # Try to generate texture using the new texture generator
        try:
            texture_result = self.texture_generator.generate_texture(prompt, reference_image_path)
            if texture_result['success']:
                logger.info("Generated texture with new texture generator")
                # In a real implementation, we would apply the texture to the mesh
                # For now, we'll just log that we generated a texture
        except Exception as e:
            logger.warning(f"Texture generator failed, using traditional texture generation: {e}")
        
        # Enhance with texture-aware modifications
        textured_mesh = self._apply_texture_aware_modifications(base_mesh, prompt, config)
        
        return textured_mesh
    
    def _analyze_prompt(self, prompt: str) -> Dict[str, Any]:
        """Analyze prompt to extract shape characteristics"""
        prompt_lower = prompt.lower()
        
        # Force simplicity flags
        shape_info = {
            'no_interior': True,
            'simple_geometry': True,
            'max_faces': 10000,  # Hard limit
            'optimize_for_game': True
        }
        
        # Shape type detection
        shape_types = {
            'vehicle': ['car', 'truck', 'motorcycle', 'bike', 'vehicle', 'automobile', 'spaceship', 'rocket', 'ship', 'boat', 'airplane', 'plane', 'helicopter'],
            'building': ['house', 'building', 'castle', 'tower', 'skyscraper', 'cottage', 'mansion', 'apartment', 'office'],
            'furniture': ['chair', 'table', 'desk', 'bed', 'sofa', 'couch', 'cabinet', 'shelf', 'lamp'],
            'character': ['person', 'human', 'robot', 'animal', 'creature', 'monster', 'dragon'],
            'weapon': ['sword', 'gun', 'rifle', 'pistol', 'knife', 'axe', 'bow', 'arrow'],
            'nature': ['tree', 'flower', 'plant', 'rock', 'mountain', 'crystal', 'gem'],
            'abstract': ['abstract', 'geometric', 'sculpture', 'art', 'design']
        }
        
        detected_shape = 'abstract'  # default
        for shape_type, keywords in shape_types.items():
            if any(keyword in prompt_lower for keyword in keywords):
                detected_shape = shape_type
                break
        
        # Style detection
        styles = {
            'realistic': ['realistic', 'photorealistic', 'detailed', 'accurate'],
            'stylized': ['stylized', 'cartoon', 'anime', 'comic', 'artistic'],
            'low_poly': ['low poly', 'low-poly', 'minimal', 'simple', 'geometric'],
            'sci_fi': ['sci-fi', 'futuristic', 'cyberpunk', 'space', 'alien'],
            'fantasy': ['fantasy', 'magical', 'medieval', 'ancient', 'mythical']
        }
        
        detected_style = 'realistic'  # default
        for style, keywords in styles.items():
            if any(keyword in prompt_lower for keyword in keywords):
                detected_style = style
                break
        
        # Size detection
        size_keywords = {
            'tiny': ['tiny', 'small', 'miniature', 'mini'],
            'normal': ['normal', 'standard', 'regular'],
            'large': ['large', 'big', 'huge', 'massive', 'giant']
        }
        
        detected_size = 'normal'  # default
        for size, keywords in size_keywords.items():
            if any(keyword in prompt_lower for keyword in keywords):
                detected_size = size
                break
        
        return {
            'shape_type': detected_shape,
            'style': detected_style,
            'size': detected_size,
            'complexity': self._estimate_complexity(prompt),
            'symmetry': 'symmetric' if any(word in prompt_lower for word in ['symmetric', 'balanced', 'even']) else 'asymmetric',
            'organic': 'organic' if any(word in prompt_lower for word in ['organic', 'natural', 'curved', 'flowing']) else 'geometric'
        }
    
    def _estimate_complexity(self, prompt: str) -> int:
        """Estimate complexity based on prompt"""
        prompt_lower = prompt.lower()
        
        # Count detail indicators
        detail_words = ['detailed', 'complex', 'intricate', 'elaborate', 'ornate', 'decorated', 'patterned']
        detail_count = sum(1 for word in detail_words if word in prompt_lower)
        
        # Count simple indicators
        simple_words = ['simple', 'basic', 'minimal', 'clean', 'plain']
        simple_count = sum(1 for word in simple_words if word in prompt_lower)
        
        # Base complexity
        base_complexity = 5
        
        # Adjust based on keywords
        complexity = base_complexity + detail_count - simple_count
        
        # Clamp to 1-10 range
        return max(1, min(10, complexity))
    
    def _generate_base_shape(self, shape_info: Dict[str, Any], config: GenerationConfig) -> trimesh.Trimesh:
        """Generate the base shape based on analyzed prompt"""
        # Reduce complexity for Roblox
        config.complexity = min(config.complexity, 5)
        config.detail_level = min(config.detail_level, 5)
        shape_type = shape_info['shape_type']
        style = shape_info['style']
        size = shape_info['size']
        
        # Size multipliers
        size_multipliers = {
            'tiny': 0.5,
            'normal': 1.0,
            'large': 2.0
        }
        
        scale = size_multipliers.get(size, 1.0)
        
        if shape_type == 'vehicle':
            return self._generate_vehicle_shape(style, scale, config)
        elif shape_type == 'building':
            return self._generate_building_shape(style, scale, config)
        elif shape_type == 'furniture':
            return self._generate_furniture_shape(style, scale, config)
        elif shape_type == 'character':
            return self._generate_character_shape(style, scale, config)
        elif shape_type == 'weapon':
            return self._generate_weapon_shape(style, scale, config)
        elif shape_type == 'nature':
            return self._generate_nature_shape(style, scale, config)
        else:
            return self._generate_abstract_shape(style, scale, config)
    
    def _generate_vehicle_shape(self, style: str, scale: float, config: GenerationConfig) -> trimesh.Trimesh:
        """Generate vehicle-like shapes"""
        if style == 'sci_fi':
            # Futuristic vehicle
            body = trimesh.creation.capsule(radius=0.8 * scale, height=4.0 * scale)
            wings = []
            
            # Add multiple wings
            for i in range(3):
                wing = trimesh.creation.box(extents=[2.5 * scale, 0.1 * scale, 0.8 * scale])
                wing.apply_translation([0, 0, (i - 1) * 0.8 * scale])
                wings.append(wing)
            
            # Add engine details
            engines = []
            for i in range(2):
                engine = trimesh.creation.cylinder(radius=0.2 * scale, height=1.0 * scale)
                engine.apply_translation([0, 0, -2.0 * scale + i * 0.5 * scale])
                engines.append(engine)
            
            parts = [body] + wings + engines
            return trimesh.util.concatenate(parts)
        
        else:
            # Standard vehicle
            body = trimesh.creation.box(extents=[3.0 * scale, 1.5 * scale, 0.8 * scale])
            cabin = trimesh.creation.box(extents=[1.5 * scale, 1.2 * scale, 0.6 * scale])
            cabin.apply_translation([0, 0, 1.2 * scale])
            
            # Wheels
            wheels = []
            wheel_positions = [
                [1.0 * scale, 0.6 * scale, 0],
                [1.0 * scale, -0.6 * scale, 0],
                [-1.0 * scale, 0.6 * scale, 0],
                [-1.0 * scale, -0.6 * scale, 0]
            ]
            
            for pos in wheel_positions:
                wheel = trimesh.creation.cylinder(radius=0.3 * scale, height=0.2 * scale)
                wheel.apply_translation(pos)
                wheels.append(wheel)
            
            parts = [body, cabin] + wheels
            return trimesh.util.concatenate(parts)
    
    def _generate_building_shape(self, style: str, scale: float, config: GenerationConfig) -> trimesh.Trimesh:
        """Generate building-like shapes"""
        if style == 'fantasy':
            # Fantasy castle
            base = trimesh.creation.cylinder(radius=2.0 * scale, height=0.5 * scale)
            tower = trimesh.creation.cylinder(radius=1.0 * scale, height=4.0 * scale)
            tower.apply_translation([0, 0, 2.25 * scale])
            
            # Cone roof
            roof = trimesh.creation.cone(radius=1.2 * scale, height=1.5 * scale)
            roof.apply_translation([0, 0, 5.25 * scale])
            
            # Small towers
            small_towers = []
            for i in range(4):
                angle = i * math.pi / 2
                x = 1.5 * scale * math.cos(angle)
                y = 1.5 * scale * math.sin(angle)
                small_tower = trimesh.creation.cylinder(radius=0.3 * scale, height=2.0 * scale)
                small_tower.apply_translation([x, y, 1.0 * scale])
                small_towers.append(small_tower)
            
            parts = [base, tower, roof] + small_towers
            return trimesh.util.concatenate(parts)
        
        else:
            # Modern building
            base = trimesh.creation.box(extents=[3.0 * scale, 3.0 * scale, 0.5 * scale])
            building = trimesh.creation.box(extents=[2.5 * scale, 2.5 * scale, 4.0 * scale])
            building.apply_translation([0, 0, 2.25 * scale])
            
            # Windows (simplified as indentations)
            windows = []
            for i in range(3):
                for j in range(3):
                    window = trimesh.creation.box(extents=[0.3 * scale, 0.1 * scale, 0.5 * scale])
                    window.apply_translation([(i - 1) * 0.8 * scale, 1.25 * scale, 2.0 * scale + j * 1.0 * scale])
                    windows.append(window)
            
            parts = [base, building] + windows
            return trimesh.util.concatenate(parts)
    
    def _generate_furniture_shape(self, style: str, scale: float, config: GenerationConfig) -> trimesh.Trimesh:
        """Generate furniture-like shapes"""
        if style == 'modern':
            # Modern chair
            seat = trimesh.creation.box(extents=[1.0 * scale, 1.0 * scale, 0.1 * scale])
            seat.apply_translation([0, 0, 0.8 * scale])
            
            backrest = trimesh.creation.box(extents=[1.0 * scale, 0.1 * scale, 1.2 * scale])
            backrest.apply_translation([0, 0.45 * scale, 1.4 * scale])
            
            # Minimalist legs
            legs = []
            leg_positions = [
                [0.4 * scale, 0.4 * scale, 0.4 * scale],
                [0.4 * scale, -0.4 * scale, 0.4 * scale],
                [-0.4 * scale, 0.4 * scale, 0.4 * scale],
                [-0.4 * scale, -0.4 * scale, 0.4 * scale]
            ]
            
            for pos in leg_positions:
                leg = trimesh.creation.cylinder(radius=0.05 * scale, height=0.8 * scale)
                leg.apply_translation(pos)
                legs.append(leg)
            
            parts = [seat, backrest] + legs
            return trimesh.util.concatenate(parts)
        
        else:
            # Traditional chair
            seat = trimesh.creation.box(extents=[1.2 * scale, 1.2 * scale, 0.15 * scale])
            seat.apply_translation([0, 0, 0.8 * scale])
            
            backrest = trimesh.creation.box(extents=[1.2 * scale, 0.15 * scale, 1.5 * scale])
            backrest.apply_translation([0, 0.525 * scale, 1.575 * scale])
            
            # Thicker legs
            legs = []
            leg_positions = [
                [0.5 * scale, 0.5 * scale, 0.4 * scale],
                [0.5 * scale, -0.5 * scale, 0.4 * scale],
                [-0.5 * scale, 0.5 * scale, 0.4 * scale],
                [-0.5 * scale, -0.5 * scale, 0.4 * scale]
            ]
            
            for pos in leg_positions:
                leg = trimesh.creation.cylinder(radius=0.08 * scale, height=0.8 * scale)
                leg.apply_translation(pos)
                legs.append(leg)
            
            parts = [seat, backrest] + legs
            return trimesh.util.concatenate(parts)
    
    def _generate_character_shape(self, style: str, scale: float, config: GenerationConfig) -> trimesh.Trimesh:
        """Generate character-like shapes"""
        if style == 'robot':
            # Robot character
            head = trimesh.creation.box(extents=[0.8 * scale, 0.8 * scale, 0.8 * scale])
            head.apply_translation([0, 0, 2.0 * scale])
            
            body = trimesh.creation.box(extents=[1.0 * scale, 0.6 * scale, 1.5 * scale])
            body.apply_translation([0, 0, 0.75 * scale])
            
            # Arms
            left_arm = trimesh.creation.cylinder(radius=0.15 * scale, height=1.2 * scale)
            left_arm.apply_translation([-0.8 * scale, 0, 1.0 * scale])
            
            right_arm = trimesh.creation.cylinder(radius=0.15 * scale, height=1.2 * scale)
            right_arm.apply_translation([0.8 * scale, 0, 1.0 * scale])
            
            # Legs
            left_leg = trimesh.creation.cylinder(radius=0.2 * scale, height=1.5 * scale)
            left_leg.apply_translation([-0.3 * scale, 0, -0.75 * scale])
            
            right_leg = trimesh.creation.cylinder(radius=0.2 * scale, height=1.5 * scale)
            right_leg.apply_translation([0.3 * scale, 0, -0.75 * scale])
            
            parts = [head, body, left_arm, right_arm, left_leg, right_leg]
            return trimesh.util.concatenate(parts)
        
        else:
            # Humanoid character
            head = trimesh.creation.uv_sphere(radius=0.4 * scale)
            head.apply_translation([0, 0, 2.0 * scale])
            
            body = trimesh.creation.capsule(radius=0.3 * scale, height=1.2 * scale)
            body.apply_translation([0, 0, 0.6 * scale])
            
            # Arms
            left_arm = trimesh.creation.capsule(radius=0.1 * scale, height=1.0 * scale)
            left_arm.apply_translation([-0.6 * scale, 0, 1.0 * scale])
            
            right_arm = trimesh.creation.capsule(radius=0.1 * scale, height=1.0 * scale)
            right_arm.apply_translation([0.6 * scale, 0, 1.0 * scale])
            
            # Legs
            left_leg = trimesh.creation.capsule(radius=0.15 * scale, height=1.2 * scale)
            left_leg.apply_translation([-0.2 * scale, 0, -0.6 * scale])
            
            right_leg = trimesh.creation.capsule(radius=0.15 * scale, height=1.2 * scale)
            right_leg.apply_translation([0.2 * scale, 0, -0.6 * scale])
            
            parts = [head, body, left_arm, right_arm, left_leg, right_leg]
            return trimesh.util.concatenate(parts)
    
    def _generate_weapon_shape(self, style: str, scale: float, config: GenerationConfig) -> trimesh.Trimesh:
        """Generate weapon-like shapes"""
        if style == 'sci_fi':
            # Sci-fi weapon
            handle = trimesh.creation.cylinder(radius=0.1 * scale, height=0.8 * scale)
            
            barrel = trimesh.creation.cylinder(radius=0.05 * scale, height=1.5 * scale)
            barrel.apply_translation([0, 0, 1.15 * scale])
            
            # Energy core
            core = trimesh.creation.uv_sphere(radius=0.2 * scale)
            core.apply_translation([0, 0, 0.4 * scale])
            
            # Scope
            scope = trimesh.creation.cylinder(radius=0.08 * scale, height=0.3 * scale)
            scope.apply_translation([0.15 * scale, 0, 0.6 * scale])
            
            parts = [handle, barrel, core, scope]
            return trimesh.util.concatenate(parts)
        
        else:
            # Traditional weapon (sword)
            handle = trimesh.creation.cylinder(radius=0.05 * scale, height=0.4 * scale)
            
            guard = trimesh.creation.box(extents=[0.3 * scale, 0.1 * scale, 0.05 * scale])
            guard.apply_translation([0, 0, 0.225 * scale])
            
            blade = trimesh.creation.box(extents=[0.02 * scale, 0.02 * scale, 1.2 * scale])
            blade.apply_translation([0, 0, 0.825 * scale])
            
            parts = [handle, guard, blade]
            return trimesh.util.concatenate(parts)
    
    def _generate_nature_shape(self, style: str, scale: float, config: GenerationConfig) -> trimesh.Trimesh:
        """Generate nature-like shapes"""
        if style == 'organic':
            # Organic tree
            trunk = trimesh.creation.cylinder(radius=0.2 * scale, height=2.0 * scale)
            
            # Multiple branches
            branches = []
            for i in range(5):
                angle = i * 2 * math.pi / 5
                x = 0.3 * scale * math.cos(angle)
                y = 0.3 * scale * math.sin(angle)
                branch = trimesh.creation.cylinder(radius=0.05 * scale, height=0.8 * scale)
                branch.apply_translation([x, y, 1.5 * scale])
                branches.append(branch)
            
            # Foliage (simplified as spheres)
            foliage = []
            for i in range(3):
                leaf = trimesh.creation.uv_sphere(radius=0.4 * scale)
                leaf.apply_translation([0, 0, 2.5 * scale + i * 0.3 * scale])
                foliage.append(leaf)
            
            parts = [trunk] + branches + foliage
            return trimesh.util.concatenate(parts)
        
        else:
            # Geometric crystal
            base = trimesh.creation.cylinder(radius=0.3 * scale, height=0.2 * scale)
            
            # Main crystal
            crystal = trimesh.creation.cone(radius=0.2 * scale, height=2.0 * scale)
            crystal.apply_translation([0, 0, 1.1 * scale])
            
            # Small crystals
            small_crystals = []
            for i in range(4):
                angle = i * math.pi / 2
                x = 0.4 * scale * math.cos(angle)
                y = 0.4 * scale * math.sin(angle)
                small_crystal = trimesh.creation.cone(radius=0.1 * scale, height=0.8 * scale)
                small_crystal.apply_translation([x, y, 0.6 * scale])
                small_crystals.append(small_crystal)
            
            parts = [base, crystal] + small_crystals
            return trimesh.util.concatenate(parts)
    
    def _generate_abstract_shape(self, style: str, scale: float, config: GenerationConfig) -> trimesh.Trimesh:
        """Generate abstract geometric shapes"""
        if style == 'low_poly':
            # Low poly abstract
            vertices = np.array([
                [0, 0, 0],
                [1 * scale, 0, 0],
                [0.5 * scale, 1 * scale, 0],
                [0.5 * scale, 0.5 * scale, 1 * scale]
            ])
            
            faces = np.array([
                [0, 1, 2],
                [0, 1, 3],
                [1, 2, 3],
                [0, 2, 3]
            ])
            
            return trimesh.Trimesh(vertices=vertices, faces=faces)
        
        else:
            # Complex abstract
            # Create multiple geometric shapes and combine them
            shapes = []
            
            # Base torus
            torus = trimesh.creation.annulus(r_min=0.5 * scale, r_max=1.0 * scale, height=0.3 * scale)
            shapes.append(torus)
            
            # Central sphere
            sphere = trimesh.creation.uv_sphere(radius=0.3 * scale)
            shapes.append(sphere)
            
            # Spiral elements
            for i in range(8):
                angle = i * math.pi / 4
                x = 0.8 * scale * math.cos(angle)
                y = 0.8 * scale * math.sin(angle)
                z = 0.2 * scale * math.sin(i * math.pi / 2)
                
                spiral = trimesh.creation.cylinder(radius=0.05 * scale, height=0.4 * scale)
                spiral.apply_translation([x, y, z])
                shapes.append(spiral)
            
            return trimesh.util.concatenate(shapes)
    
    def _add_details(self, base_mesh: trimesh.Trimesh, shape_info: Dict[str, Any], config: GenerationConfig) -> trimesh.Trimesh:
        """Add details to the base mesh based on complexity"""
        if config.complexity <= 3:
            return base_mesh  # Keep simple
        
        detailed_mesh = base_mesh.copy()
        
        # Add surface details based on complexity
        if config.complexity >= 7:
            detailed_mesh = self._add_surface_details(detailed_mesh, config)
        
        if config.complexity >= 8:
            detailed_mesh = self._add_structural_details(detailed_mesh, shape_info, config)
        
        if config.complexity >= 9:
            detailed_mesh = self._add_fine_details(detailed_mesh, config)
        
        return detailed_mesh
    
    def _add_surface_details(self, mesh: trimesh.Trimesh, config: GenerationConfig) -> trimesh.Trimesh:
        """Add surface details like bumps and indentations"""
        # This is a simplified version - in a real implementation,
        # you'd use displacement mapping or subdivision surfaces
        
        # Add small geometric details
        details = []
        
        # Create small bumps on the surface
        for i in range(20):
            # Random position on the mesh surface
            point = mesh.sample(1)[0]
            
            # Small bump
            bump = trimesh.creation.uv_sphere(radius=0.05)
            bump.apply_translation(point)
            details.append(bump)
        
        if details:
            return trimesh.util.concatenate([mesh] + details)
        
        return mesh
    
    def _add_structural_details(self, mesh: trimesh.Trimesh, shape_info: Dict[str, Any], config: GenerationConfig) -> trimesh.Trimesh:
        """Add structural details like panels, seams, etc."""
        details = []
        
        # Add panel lines
        if shape_info['shape_type'] in ['vehicle', 'building', 'robot']:
            # Create panel lines
            for i in range(5):
                panel = trimesh.creation.box(extents=[0.01, 0.5, 0.01])
                panel.apply_translation([0, (i - 2) * 0.3, 0])
                details.append(panel)
        
        if details:
            return trimesh.util.concatenate([mesh] + details)
        
        return mesh
    
    def _add_fine_details(self, mesh: trimesh.Trimesh, config: GenerationConfig) -> trimesh.Trimesh:
        """Add very fine details for high complexity"""
        # This would include things like screws, bolts, fine textures, etc.
        # For now, we'll add some small geometric elements
        
        details = []
        
        # Add small decorative elements
        for i in range(10):
            detail = trimesh.creation.cylinder(radius=0.02, height=0.1)
            detail.apply_translation([
                random.uniform(-1, 1),
                random.uniform(-1, 1),
                random.uniform(-1, 1)
            ])
            details.append(detail)
        
        if details:
            return trimesh.util.concatenate([mesh] + details)
        
        return mesh
    
    def _apply_transformations(self, mesh: trimesh.Trimesh, shape_info: Dict[str, Any], config: GenerationConfig) -> trimesh.Trimesh:
        """Apply final transformations to the mesh"""
        transformed_mesh = mesh.copy()
        
        # Apply style-based transformations
        if shape_info['style'] == 'stylized':
            # Exaggerate proportions
            transformed_mesh.apply_scale([1.2, 1.2, 1.0])
        
        elif shape_info['style'] == 'low_poly':
            # Simplify mesh
            transformed_mesh = self._simplify_mesh(transformed_mesh, target_faces=100)
        
        # Apply organic transformations if needed
        if shape_info['organic'] == 'organic':
            transformed_mesh = self._make_organic(transformed_mesh)
        
        # Apply asymmetry if needed
        if shape_info['symmetry'] == 'asymmetric':
            transformed_mesh = self._make_asymmetric(transformed_mesh)
        
        return transformed_mesh
    
    def _simplify_mesh(self, mesh: trimesh.Trimesh, target_faces: int) -> trimesh.Trimesh:
        """Simplify mesh to target number of faces"""
        if len(mesh.faces) <= target_faces:
            return mesh
        
        # Simple decimation (in a real implementation, you'd use proper mesh decimation)
        # For now, we'll just return the original mesh
        return mesh
    
    def _make_organic(self, mesh: trimesh.Trimesh) -> trimesh.Trimesh:
        """Make the mesh more organic by adding noise"""
        # Add some random noise to vertices
        vertices = mesh.vertices.copy()
        noise = np.random.normal(0, 0.05, vertices.shape)
        vertices += noise
        
        return trimesh.Trimesh(vertices=vertices, faces=mesh.faces)
    
    def _make_asymmetric(self, mesh: trimesh.Trimesh) -> trimesh.Trimesh:
        """Make the mesh asymmetric"""
        # Apply slight random scaling
        scale_factors = np.random.uniform(0.9, 1.1, 3)
        mesh.apply_scale(scale_factors)
        
        return mesh
    
    def _enhanced_procedural_generation(self, prompt: str, config: GenerationConfig, reference_image_path: Optional[str] = None) -> trimesh.Trimesh:
        """Enhanced procedural generation with more sophisticated algorithms"""
        # This would use more advanced procedural generation techniques
        # For now, we'll use the basic procedural generation but with higher complexity
        
        enhanced_config = GenerationConfig(
            engine=config.engine,
            complexity=min(10, config.complexity + 2),
            detail_level=min(10, config.detail_level + 2),
            material_style=config.material_style,
            generate_textures=config.generate_textures,
            generate_materials=config.generate_materials,
            variations=config.variations,
            seed=config.seed
        )
        
        return self._procedural_generation(prompt, enhanced_config, reference_image_path)
    
    def _apply_texture_aware_modifications(self, mesh: trimesh.Trimesh, prompt: str, config: GenerationConfig) -> trimesh.Trimesh:
        """Apply modifications that are aware of texture generation"""
        # This would modify the mesh to be more suitable for texture generation
        # For example, ensuring proper UV mapping, adding texture seams, etc.
        
        # For now, we'll just return the original mesh
        return mesh
    
    def _generate_textures(self, prompt: str, config: GenerationConfig) -> Dict[str, Any]:
        """Generate textures for the model"""
        # Try to generate textures using the new texture generator
        try:
            texture_result = self.texture_generator.generate_texture(prompt)
            if texture_result['success']:
                logger.info("Generated textures with new texture generator")
                # In a real implementation, we would save the textures to files
                # For now, we'll just return placeholder paths
                return {
                    'diffuse': 'generated/diffuse.png',
                    'normal': 'generated/normal.png',
                    'roughness': 'generated/roughness.png',
                    'metallic': 'generated/metallic.png'
                }
        except Exception as e:
            logger.warning(f"Texture generator failed, using placeholder textures: {e}")
        
        # Fallback to placeholder texture information
        return {
            'diffuse': 'generated/diffuse.png',
            'normal': 'generated/normal.png',
            'roughness': 'generated/roughness.png',
            'metallic': 'generated/metallic.png'
        }
    
    def _generate_materials(self, prompt: str, config: GenerationConfig) -> Dict[str, Any]:
        """Generate material definitions"""
        # This would create material definitions for various renderers
        
        return {
            'pbr': {
                'base_color': [0.8, 0.8, 0.8],
                'metallic': 0.0,
                'roughness': 0.5,
                'normal_scale': 1.0
            },
            'blender': {
                'shader': 'Principled BSDF',
                'parameters': {
                    'Base Color': [0.8, 0.8, 0.8, 1.0],
                    'Metallic': 0.0,
                    'Roughness': 0.5
                }
            }
        }
    
    def _generate_metadata(self, prompt: str, config: GenerationConfig, mesh: trimesh.Trimesh) -> Dict[str, Any]:
        """Generate metadata about the generated model"""
        return {
            'prompt': prompt,
            'engine': config.engine.value,
            'complexity': config.complexity,
            'detail_level': config.detail_level,
            'material_style': config.material_style,
            'vertex_count': len(mesh.vertices),
            'face_count': len(mesh.faces),
            'bounds': mesh.bounds.tolist(),
            'volume': mesh.volume,
            'surface_area': mesh.area,
            'generation_time': time.time(),
            'seed': config.seed
        }
    
    def _has_ai_api_access(self) -> bool:
        """Check if we have access to external AI APIs"""
        # Check for API keys or configuration
        return False  # For now, return False
    
    def _call_external_ai_api(self, prompt: str, config: GenerationConfig, reference_image_path: Optional[str] = None) -> trimesh.Trimesh:
        """Call external AI API for model generation"""
        # This would integrate with services like OpenAI, Stability AI, etc.
        # For now, raise an exception to trigger fallback
        raise NotImplementedError("External AI API not configured")
    
    def _select_best_mesh(self, meshes: List[trimesh.Trimesh], prompt: str, config: GenerationConfig) -> trimesh.Trimesh:
        """Select the best mesh from multiple candidates"""
        # Simple selection based on complexity and quality
        # In a real implementation, you'd use more sophisticated metrics
        
        best_mesh = meshes[0]
        best_score = self._calculate_mesh_quality(meshes[0], prompt, config)
        
        for mesh in meshes[1:]:
            score = self._calculate_mesh_quality(mesh, prompt, config)
            if score > best_score:
                best_score = score
                best_mesh = mesh
        
        return best_mesh
    
    def _calculate_mesh_quality(self, mesh: trimesh.Trimesh, prompt: str, config: GenerationConfig) -> float:
        """Calculate quality score for a mesh"""
        # Simple quality metric based on complexity and detail
        vertex_score = min(len(mesh.vertices) / 1000, 1.0)  # Normalize vertex count
        face_score = min(len(mesh.faces) / 500, 1.0)  # Normalize face count
        volume_score = min(mesh.volume / 10, 1.0)  # Normalize volume
        
        return (vertex_score + face_score + volume_score) / 3.0
