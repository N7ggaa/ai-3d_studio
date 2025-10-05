#!/usr/bin/env python3
"""
AI Integration Module for ModelForge
Connects to various AI services for enhanced 3D model generation
"""

import os
import logging
import requests
import json
import time
import base64
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import openai
import trimesh
import numpy as np

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIService(Enum):
    """Available AI services"""
    OPENAI = "openai"
    STABILITY_AI = "stability_ai"
    MIDJOURNEY = "midjourney"
    DALL_E = "dall_e"
    CUSTOM_API = "custom_api"

@dataclass
class AIConfig:
    """Configuration for AI service"""
    service: AIService
    api_key: str
    model: str = "gpt-4"
    max_tokens: int = 2000
    temperature: float = 0.7
    timeout: int = 30

class AIIntegration:
    """AI integration for enhanced 3D model generation"""
    
    def __init__(self, config: AIConfig):
        self.config = config
        self.setup_service()
    
    def setup_service(self):
        """Setup the AI service based on configuration"""
        if self.config.service == AIService.OPENAI:
            openai.api_key = self.config.api_key
        elif self.config.service == AIService.STABILITY_AI:
            # Setup Stability AI client
            pass
        elif self.config.service == AIService.CUSTOM_API:
            # Setup custom API client
            pass
    
    def generate_3d_from_prompt(self, prompt: str, reference_image_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate 3D model using AI service
        
        Args:
            prompt: Text description
            reference_image_path: Optional reference image
            
        Returns:
            Dict containing generation results
        """
        try:
            if self.config.service == AIService.OPENAI:
                return self._generate_with_openai(prompt, reference_image_path)
            elif self.config.service == AIService.STABILITY_AI:
                return self._generate_with_stability_ai(prompt, reference_image_path)
            elif self.config.service == AIService.CUSTOM_API:
                return self._generate_with_custom_api(prompt, reference_image_path)
            else:
                raise ValueError(f"Unsupported AI service: {self.config.service}")
                
        except Exception as e:
            logger.error(f"AI generation failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'fallback': True
            }
    
    def _generate_with_openai(self, prompt: str, reference_image_path: Optional[str] = None) -> Dict[str, Any]:
        """Generate using OpenAI's API"""
        try:
            # Enhanced prompt engineering
            enhanced_prompt = self._enhance_prompt_for_3d(prompt)
            
            # Generate detailed description
            description_response = openai.ChatCompletion.create(
                model=self.config.model,
                messages=[
                    {"role": "system", "content": "You are a 3D modeling expert. Generate detailed technical specifications for creating a 3D model based on the user's description."},
                    {"role": "user", "content": enhanced_prompt}
                ],
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature
            )
            
            detailed_description = description_response.choices[0].message.content
            
            # Generate mesh parameters
            mesh_params = self._extract_mesh_parameters(detailed_description)
            
            # Generate the actual 3D mesh
            mesh = self._generate_mesh_from_params(mesh_params, prompt)
            
            return {
                'success': True,
                'mesh': mesh,
                'description': detailed_description,
                'parameters': mesh_params,
                'service': 'openai'
            }
            
        except Exception as e:
            logger.error(f"OpenAI generation failed: {e}")
            raise
    
    def _generate_with_stability_ai(self, prompt: str, reference_image_path: Optional[str] = None) -> Dict[str, Any]:
        """Generate using Stability AI's API"""
        try:
            # This would integrate with Stability AI's 3D generation API
            # For now, return a placeholder
            raise NotImplementedError("Stability AI integration not yet implemented")
            
        except Exception as e:
            logger.error(f"Stability AI generation failed: {e}")
            raise
    
    def _generate_with_custom_api(self, prompt: str, reference_image_path: Optional[str] = None) -> Dict[str, Any]:
        """Generate using custom API"""
        try:
            # Custom API integration
            api_url = os.environ.get('CUSTOM_AI_API_URL')
            api_key = os.environ.get('CUSTOM_AI_API_KEY')
            
            if not api_url or not api_key:
                raise ValueError("Custom API configuration not found")
            
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'prompt': prompt,
                'reference_image': self._encode_image(reference_image_path) if reference_image_path else None,
                'parameters': {
                    'quality': 'high',
                    'format': 'obj',
                    'include_textures': True
                }
            }
            
            response = requests.post(
                api_url,
                headers=headers,
                json=payload,
                timeout=self.config.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'mesh': self._parse_custom_api_response(result),
                    'service': 'custom_api'
                }
            else:
                raise Exception(f"Custom API error: {response.status_code} - {response.text}")
                
        except Exception as e:
            logger.error(f"Custom API generation failed: {e}")
            raise
    
    def _enhance_prompt_for_3d(self, prompt: str) -> str:
        """Enhance prompt for better 3D generation"""
        enhancement_template = """
        Please analyze this 3D model description and provide detailed technical specifications:
        
        Original prompt: {prompt}
        
        Please provide:
        1. Shape type and category
        2. Dimensions and proportions
        3. Surface details and textures
        4. Material properties
        5. Geometric complexity level
        6. Specific features and components
        7. Style and aesthetic details
        
        Format the response as structured data that can be used for 3D mesh generation.
        """
        
        return enhancement_template.format(prompt=prompt)
    
    def _extract_mesh_parameters(self, description: str) -> Dict[str, Any]:
        """Extract mesh generation parameters from AI description"""
        # Parse the AI-generated description to extract parameters
        # This is a simplified version - in practice, you'd use more sophisticated parsing
        
        params = {
            'shape_type': 'abstract',
            'dimensions': [1.0, 1.0, 1.0],
            'complexity': 5,
            'materials': ['default'],
            'features': [],
            'style': 'realistic'
        }
        
        description_lower = description.lower()
        
        # Extract shape type
        if 'vehicle' in description_lower or 'car' in description_lower:
            params['shape_type'] = 'vehicle'
        elif 'building' in description_lower or 'house' in description_lower:
            params['shape_type'] = 'building'
        elif 'character' in description_lower or 'person' in description_lower:
            params['shape_type'] = 'character'
        elif 'weapon' in description_lower or 'sword' in description_lower:
            params['shape_type'] = 'weapon'
        elif 'furniture' in description_lower or 'chair' in description_lower:
            params['shape_type'] = 'furniture'
        elif 'nature' in description_lower or 'tree' in description_lower:
            params['shape_type'] = 'nature'
        
        # Extract complexity
        if 'complex' in description_lower or 'detailed' in description_lower:
            params['complexity'] = 8
        elif 'simple' in description_lower or 'basic' in description_lower:
            params['complexity'] = 3
        
        # Extract style
        if 'stylized' in description_lower or 'cartoon' in description_lower:
            params['style'] = 'stylized'
        elif 'realistic' in description_lower or 'photorealistic' in description_lower:
            params['style'] = 'realistic'
        elif 'low poly' in description_lower:
            params['style'] = 'low_poly'
        
        return params
    
    def _generate_mesh_from_params(self, params: Dict[str, Any], original_prompt: str) -> trimesh.Trimesh:
        """Generate mesh from extracted parameters"""
        # This would use the parameters to generate a more sophisticated mesh
        # For now, we'll create a basic mesh based on the parameters
        
        shape_type = params['shape_type']
        complexity = params['complexity']
        style = params['style']
        
        # Create base mesh based on shape type
        if shape_type == 'vehicle':
            mesh = self._create_vehicle_mesh(complexity, style)
        elif shape_type == 'building':
            mesh = self._create_building_mesh(complexity, style)
        elif shape_type == 'character':
            mesh = self._create_character_mesh(complexity, style)
        elif shape_type == 'weapon':
            mesh = self._create_weapon_mesh(complexity, style)
        elif shape_type == 'furniture':
            mesh = self._create_furniture_mesh(complexity, style)
        elif shape_type == 'nature':
            mesh = self._create_nature_mesh(complexity, style)
        else:
            mesh = self._create_abstract_mesh(complexity, style)
        
        # Apply complexity-based modifications
        mesh = self._apply_complexity_modifications(mesh, complexity)
        
        return mesh
    
    def _create_vehicle_mesh(self, complexity: int, style: str) -> trimesh.Trimesh:
        """Create vehicle mesh with AI-enhanced details"""
        # Create sophisticated vehicle mesh
        body = trimesh.creation.capsule(radius=0.8, height=3.0)
        
        # Add wings based on complexity
        wings = []
        wing_count = min(complexity // 2, 4)  # More complexity = more wings
        
        for i in range(wing_count):
            wing = trimesh.creation.box(extents=[2.0, 0.1, 0.6])
            wing.apply_translation([0, 0, (i - wing_count//2) * 0.8])
            wings.append(wing)
        
        # Add engines
        engines = []
        for i in range(2):
            engine = trimesh.creation.cylinder(radius=0.2, height=1.0)
            engine.apply_translation([0, 0, -1.5 + i * 0.3])
            engines.append(engine)
        
        # Add cockpit
        cockpit = trimesh.creation.uv_sphere(radius=0.4)
        cockpit.apply_translation([0, 0, 1.5])
        
        parts = [body, cockpit] + wings + engines
        return trimesh.util.concatenate(parts)
    
    def _create_building_mesh(self, complexity: int, style: str) -> trimesh.Trimesh:
        """Create building mesh with AI-enhanced details"""
        # Create sophisticated building mesh
        base = trimesh.creation.cylinder(radius=2.0, height=0.5)
        
        # Main structure
        floors = min(complexity // 2, 8)  # More complexity = more floors
        building = trimesh.creation.box(extents=[3.0, 3.0, floors * 0.8])
        building.apply_translation([0, 0, floors * 0.4 + 0.25])
        
        # Add windows
        windows = []
        for floor in range(floors):
            for side in range(4):
                for window in range(3):
                    angle = side * np.pi / 2
                    x = 1.5 * np.cos(angle)
                    y = 1.5 * np.sin(angle)
                    z = floor * 0.8 + 0.4
                    
                    window_mesh = trimesh.creation.box(extents=[0.2, 0.1, 0.4])
                    window_mesh.apply_translation([x, y, z])
                    windows.append(window_mesh)
        
        # Add roof details
        roof = trimesh.creation.cone(radius=2.2, height=1.0)
        roof.apply_translation([0, 0, floors * 0.8 + 0.5])
        
        parts = [base, building, roof] + windows
        return trimesh.util.concatenate(parts)
    
    def _create_character_mesh(self, complexity: int, style: str) -> trimesh.Trimesh:
        """Create character mesh with AI-enhanced details"""
        # Create sophisticated character mesh
        head = trimesh.creation.uv_sphere(radius=0.4)
        head.apply_translation([0, 0, 2.0])
        
        body = trimesh.creation.capsule(radius=0.3, height=1.2)
        body.apply_translation([0, 0, 0.6])
        
        # Add limbs
        limbs = []
        
        # Arms
        for side in [-1, 1]:
            arm = trimesh.creation.capsule(radius=0.1, height=1.0)
            arm.apply_translation([side * 0.6, 0, 1.0])
            limbs.append(arm)
        
        # Legs
        for side in [-1, 1]:
            leg = trimesh.creation.capsule(radius=0.15, height=1.2)
            leg.apply_translation([side * 0.2, 0, -0.6])
            limbs.append(leg)
        
        # Add details based on complexity
        if complexity >= 7:
            # Add hands
            for side in [-1, 1]:
                hand = trimesh.creation.uv_sphere(radius=0.08)
                hand.apply_translation([side * 0.6, 0, 1.5])
                limbs.append(hand)
        
        if complexity >= 8:
            # Add feet
            for side in [-1, 1]:
                foot = trimesh.creation.box(extents=[0.2, 0.3, 0.1])
                foot.apply_translation([side * 0.2, 0, -1.2])
                limbs.append(foot)
        
        parts = [head, body] + limbs
        return trimesh.util.concatenate(parts)
    
    def _create_weapon_mesh(self, complexity: int, style: str) -> trimesh.Trimesh:
        """Create weapon mesh with AI-enhanced details"""
        # Create sophisticated weapon mesh
        handle = trimesh.creation.cylinder(radius=0.1, height=0.8)
        
        guard = trimesh.creation.box(extents=[0.4, 0.1, 0.05])
        guard.apply_translation([0, 0, 0.425])
        
        blade = trimesh.creation.box(extents=[0.02, 0.02, 1.5])
        blade.apply_translation([0, 0, 1.175])
        
        # Add details based on complexity
        details = []
        
        if complexity >= 6:
            # Add pommel
            pommel = trimesh.creation.uv_sphere(radius=0.15)
            pommel.apply_translation([0, 0, -0.075])
            details.append(pommel)
        
        if complexity >= 7:
            # Add blade fuller
            fuller = trimesh.creation.box(extents=[0.01, 0.01, 1.0])
            fuller.apply_translation([0, 0, 0.925])
            details.append(fuller)
        
        if complexity >= 8:
            # Add decorative elements
            for i in range(3):
                decoration = trimesh.creation.cylinder(radius=0.02, height=0.1)
                decoration.apply_translation([0, 0, 0.2 + i * 0.2])
                details.append(decoration)
        
        parts = [handle, guard, blade] + details
        return trimesh.util.concatenate(parts)
    
    def _create_furniture_mesh(self, complexity: int, style: str) -> trimesh.Trimesh:
        """Create furniture mesh with AI-enhanced details"""
        # Create sophisticated furniture mesh
        seat = trimesh.creation.box(extents=[1.0, 1.0, 0.1])
        seat.apply_translation([0, 0, 0.8])
        
        backrest = trimesh.creation.box(extents=[1.0, 0.1, 1.2])
        backrest.apply_translation([0, 0.45, 1.4])
        
        # Add legs
        legs = []
        leg_positions = [
            [0.4, 0.4, 0.4],
            [0.4, -0.4, 0.4],
            [-0.4, 0.4, 0.4],
            [-0.4, -0.4, 0.4]
        ]
        
        for pos in leg_positions:
            leg = trimesh.creation.cylinder(radius=0.05, height=0.8)
            leg.apply_translation(pos)
            legs.append(leg)
        
        # Add details based on complexity
        details = []
        
        if complexity >= 6:
            # Add armrests
            for side in [-1, 1]:
                armrest = trimesh.creation.box(extents=[0.8, 0.1, 0.1])
                armrest.apply_translation([0, side * 0.5, 1.0])
                details.append(armrest)
        
        if complexity >= 7:
            # Add cushions
            cushion = trimesh.creation.box(extents=[0.9, 0.9, 0.05])
            cushion.apply_translation([0, 0, 0.875])
            details.append(cushion)
        
        parts = [seat, backrest] + legs + details
        return trimesh.util.concatenate(parts)
    
    def _create_nature_mesh(self, complexity: int, style: str) -> trimesh.Trimesh:
        """Create nature mesh with AI-enhanced details"""
        # Create sophisticated nature mesh
        trunk = trimesh.creation.cylinder(radius=0.2, height=2.0)
        
        # Add branches
        branches = []
        branch_count = min(complexity // 2, 6)
        
        for i in range(branch_count):
            angle = i * 2 * np.pi / branch_count
            x = 0.3 * np.cos(angle)
            y = 0.3 * np.sin(angle)
            z = 1.5 + (i % 2) * 0.3
            
            branch = trimesh.creation.cylinder(radius=0.05, height=0.8)
            branch.apply_translation([x, y, z])
            branches.append(branch)
        
        # Add foliage
        foliage = []
        leaf_count = min(complexity * 2, 12)
        
        for i in range(leaf_count):
            angle = i * 2 * np.pi / leaf_count
            radius = 0.4 + (i % 3) * 0.2
            x = radius * np.cos(angle)
            y = radius * np.sin(angle)
            z = 2.5 + (i % 4) * 0.2
            
            leaf = trimesh.creation.uv_sphere(radius=0.3)
            leaf.apply_translation([x, y, z])
            foliage.append(leaf)
        
        parts = [trunk] + branches + foliage
        return trimesh.util.concatenate(parts)
    
    def _create_abstract_mesh(self, complexity: int, style: str) -> trimesh.Trimesh:
        """Create abstract mesh with AI-enhanced details"""
        # Create sophisticated abstract mesh
        shapes = []
        
        # Base shape
        if style == 'low_poly':
            # Low poly abstract
            vertices = np.array([
                [0, 0, 0],
                [1, 0, 0],
                [0.5, 1, 0],
                [0.5, 0.5, 1]
            ])
            
            faces = np.array([
                [0, 1, 2],
                [0, 1, 3],
                [1, 2, 3],
                [0, 2, 3]
            ])
            
            base = trimesh.Trimesh(vertices=vertices, faces=faces)
            shapes.append(base)
        else:
            # Complex abstract
            torus = trimesh.creation.annulus(r_min=0.5, r_max=1.0, height=0.3)
            shapes.append(torus)
            
            sphere = trimesh.creation.uv_sphere(radius=0.3)
            shapes.append(sphere)
        
        # Add complexity-based elements
        if complexity >= 6:
            # Add spiral elements
            for i in range(8):
                angle = i * np.pi / 4
                x = 0.8 * np.cos(angle)
                y = 0.8 * np.sin(angle)
                z = 0.2 * np.sin(i * np.pi / 2)
                
                spiral = trimesh.creation.cylinder(radius=0.05, height=0.4)
                spiral.apply_translation([x, y, z])
                shapes.append(spiral)
        
        if complexity >= 8:
            # Add floating elements
            for i in range(5):
                element = trimesh.creation.uv_sphere(radius=0.1)
                element.apply_translation([
                    np.random.uniform(-1, 1),
                    np.random.uniform(-1, 1),
                    np.random.uniform(-1, 1)
                ])
                shapes.append(element)
        
        return trimesh.util.concatenate(shapes)
    
    def _apply_complexity_modifications(self, mesh: trimesh.Trimesh, complexity: int) -> trimesh.Trimesh:
        """Apply complexity-based modifications to the mesh"""
        if complexity <= 3:
            return mesh  # Keep simple
        
        modified_mesh = mesh.copy()
        
        # Add surface details
        if complexity >= 6:
            # Add small geometric details
            details = []
            detail_count = complexity * 2
            
            for i in range(detail_count):
                point = mesh.sample(1)[0]
                detail = trimesh.creation.uv_sphere(radius=0.02)
                detail.apply_translation(point)
                details.append(detail)
            
            if details:
                modified_mesh = trimesh.util.concatenate([modified_mesh] + details)
        
        # Add noise for organic feel
        if complexity >= 7:
            vertices = modified_mesh.vertices.copy()
            noise = np.random.normal(0, 0.01 * complexity, vertices.shape)
            vertices += noise
            modified_mesh = trimesh.Trimesh(vertices=vertices, faces=modified_mesh.faces)
        
        return modified_mesh
    
    def _encode_image(self, image_path: str) -> Optional[str]:
        """Encode image to base64 for API transmission"""
        try:
            with open(image_path, 'rb') as image_file:
                encoded = base64.b64encode(image_file.read()).decode('utf-8')
                return encoded
        except Exception as e:
            logger.error(f"Failed to encode image: {e}")
            return None
    
    def _parse_custom_api_response(self, response: Dict[str, Any]) -> trimesh.Trimesh:
        """Parse custom API response into trimesh object"""
        # This would parse the custom API response
        # For now, return a simple mesh
        return trimesh.creation.box(extents=[1, 1, 1])

class AIServiceManager:
    """Manager for multiple AI services"""
    
    def __init__(self):
        self.services = {}
        self.setup_services()
    
    def setup_services(self):
        """Setup available AI services"""
        # Setup OpenAI if API key is available
        openai_key = os.environ.get('OPENAI_API_KEY')
        if openai_key:
            openai_config = AIConfig(
                service=AIService.OPENAI,
                api_key=openai_key,
                model="gpt-4"
            )
            self.services[AIService.OPENAI] = AIIntegration(openai_config)
        
        # Setup Stability AI if API key is available
        stability_key = os.environ.get('STABILITY_API_KEY')
        if stability_key:
            stability_config = AIConfig(
                service=AIService.STABILITY_AI,
                api_key=stability_key
            )
            self.services[AIService.STABILITY_AI] = AIIntegration(stability_config)
        
        # Setup custom API if configured
        custom_api_url = os.environ.get('CUSTOM_AI_API_URL')
        custom_api_key = os.environ.get('CUSTOM_AI_API_KEY')
        if custom_api_url and custom_api_key:
            custom_config = AIConfig(
                service=AIService.CUSTOM_API,
                api_key=custom_api_key
            )
            self.services[AIService.CUSTOM_API] = AIIntegration(custom_config)
    
    def get_available_services(self) -> List[AIService]:
        """Get list of available AI services"""
        return list(self.services.keys())
    
    def generate_with_best_service(self, prompt: str, reference_image_path: Optional[str] = None) -> Dict[str, Any]:
        """Generate using the best available service"""
        if not self.services:
            return {
                'success': False,
                'error': 'No AI services configured',
                'fallback': True
            }
        
        # Try services in order of preference
        preferred_order = [
            AIService.OPENAI,
            AIService.STABILITY_AI,
            AIService.CUSTOM_API
        ]
        
        for service in preferred_order:
            if service in self.services:
                try:
                    result = self.services[service].generate_3d_from_prompt(prompt, reference_image_path)
                    if result['success']:
                        return result
                except Exception as e:
                    logger.warning(f"Service {service} failed: {e}")
                    continue
        
        # All services failed
        return {
            'success': False,
            'error': 'All AI services failed',
            'fallback': True
        }
    
    def generate_with_specific_service(self, service: AIService, prompt: str, reference_image_path: Optional[str] = None) -> Dict[str, Any]:
        """Generate using a specific service"""
        if service not in self.services:
            return {
                'success': False,
                'error': f'Service {service} not available',
                'fallback': True
            }
        
        try:
            return self.services[service].generate_3d_from_prompt(prompt, reference_image_path)
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'fallback': True
            }
