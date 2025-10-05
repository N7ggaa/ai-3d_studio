import os
import json
import logging
import numpy as np
import trimesh
from typing import Dict, List, Optional, Tuple
from pathlib import Path


class MaterialGenerator:
    """Generate materials and textures for 3D models"""

    def __init__(self):
        self.material_library = self._load_material_library()
        self.texture_cache = {}

    def _load_material_library(self) -> Dict:
        """Load predefined material configurations"""
        return {
            'metal': {
                'diffuse': [0.7, 0.7, 0.8],
                'specular': [0.9, 0.9, 0.9],
                'roughness': 0.1,
                'metallic': 1.0,
                'emissive': [0.0, 0.0, 0.0]
            },
            'plastic': {
                'diffuse': [0.8, 0.3, 0.8],
                'specular': [0.1, 0.1, 0.1],
                'roughness': 0.3,
                'metallic': 0.0,
                'emissive': [0.0, 0.0, 0.0]
            },
            'wood': {
                'diffuse': [0.6, 0.4, 0.2],
                'specular': [0.1, 0.1, 0.1],
                'roughness': 0.8,
                'metallic': 0.0,
                'emissive': [0.0, 0.0, 0.0]
            },
            'stone': {
                'diffuse': [0.5, 0.5, 0.5],
                'specular': [0.2, 0.2, 0.2],
                'roughness': 0.9,
                'metallic': 0.0,
                'emissive': [0.0, 0.0, 0.0]
            },
            'glass': {
                'diffuse': [0.9, 0.9, 0.9],
                'specular': [1.0, 1.0, 1.0],
                'roughness': 0.0,
                'metallic': 0.0,
                'emissive': [0.0, 0.0, 0.0],
                'alpha': 0.1
            },
            'fabric': {
                'diffuse': [0.8, 0.2, 0.4],
                'specular': [0.0, 0.0, 0.0],
                'roughness': 1.0,
                'metallic': 0.0,
                'emissive': [0.0, 0.0, 0.0]
            }
        }

    def generate_material_for_prompt(self, prompt: str, style: str = "realistic") -> Dict:
        """
        Generate material properties based on text prompt

        Args:
            prompt: Text description of desired material
            style: Material style (realistic, cartoon, sci_fi, etc.)

        Returns:
            Dictionary containing material properties
        """
        prompt_lower = prompt.lower()

        # Detect material type from prompt
        if any(word in prompt_lower for word in ['metal', 'steel', 'iron', 'chrome', 'silver', 'gold']):
            base_material = self.material_library['metal'].copy()
            if 'gold' in prompt_lower:
                base_material['diffuse'] = [0.9, 0.7, 0.1]
            elif 'silver' in prompt_lower:
                base_material['diffuse'] = [0.8, 0.8, 0.9]
        elif any(word in prompt_lower for word in ['plastic', 'rubber', 'polymer']):
            base_material = self.material_library['plastic'].copy()
        elif any(word in prompt_lower for word in ['wood', 'wooden', 'oak', 'pine']):
            base_material = self.material_library['wood'].copy()
        elif any(word in prompt_lower for word in ['stone', 'rock', 'marble', 'granite']):
            base_material = self.material_library['stone'].copy()
        elif any(word in prompt_lower for word in ['glass', 'crystal', 'transparent']):
            base_material = self.material_library['glass'].copy()
        elif any(word in prompt_lower for word in ['fabric', 'cloth', 'textile', 'leather']):
            base_material = self.material_library['fabric'].copy()
        else:
            # Default material
            base_material = self.material_library['plastic'].copy()

        # Apply style modifications
        if style == "cartoon":
            base_material['roughness'] = min(1.0, base_material['roughness'] + 0.2)
            base_material['specular'] = [min(1.0, s + 0.3) for s in base_material['specular']]
        elif style == "sci_fi":
            base_material['emissive'] = [0.1, 0.1, 0.2]
            base_material['metallic'] = min(1.0, base_material['metallic'] + 0.2)
        elif style == "fantasy":
            # Add magical glow
            base_material['emissive'] = [0.2, 0.1, 0.3]

        # Add procedural variations
        base_material = self._add_material_variation(base_material)

        return base_material

    def _add_material_variation(self, material: Dict) -> Dict:
        """Add random variation to material properties"""
        # Add slight random variation to make each material unique
        variation_factor = 0.1

        for key in ['diffuse', 'specular', 'emissive']:
            if isinstance(material[key], list):
                material[key] = [
                    max(0.0, min(1.0, val + (np.random.random() - 0.5) * variation_factor))
                    for val in material[key]
                ]

        # Vary roughness and metallic slightly
        material['roughness'] = max(0.0, min(1.0,
            material['roughness'] + (np.random.random() - 0.5) * 0.1))
        material['metallic'] = max(0.0, min(1.0,
            material['metallic'] + (np.random.random() - 0.5) * 0.05))

        return material

    def generate_texture_coordinates(self, mesh: trimesh.Trimesh, texture_type: str = "procedural") -> np.ndarray:
        """
        Generate texture coordinates for a mesh

        Args:
            mesh: Input mesh
            texture_type: Type of texture mapping

        Returns:
            Array of texture coordinates
        """
        if texture_type == "spherical":
            return self._generate_spherical_uv(mesh)
        elif texture_type == "cylindrical":
            return self._generate_cylindrical_uv(mesh)
        elif texture_type == "planar":
            return self._generate_planar_uv(mesh)
        else:
            return self._generate_procedural_uv(mesh)

    def _generate_spherical_uv(self, mesh: trimesh.Trimesh) -> np.ndarray:
        """Generate spherical UV mapping"""
        vertices = mesh.vertices
        uv_coords = []

        for vertex in vertices:
            # Normalize vertex position
            if np.linalg.norm(vertex) > 0:
                normalized = vertex / np.linalg.norm(vertex)
            else:
                normalized = vertex

            # Convert to UV coordinates
            u = 0.5 + (np.arctan2(normalized[2], normalized[0]) / (2 * np.pi))
            v = 0.5 - (np.arcsin(normalized[1]) / np.pi)

            uv_coords.append([u, v])

        return np.array(uv_coords)

    def _generate_cylindrical_uv(self, mesh: trimesh.Trimesh) -> np.ndarray:
        """Generate cylindrical UV mapping"""
        vertices = mesh.vertices
        uv_coords = []

        for vertex in vertices:
            # Calculate angle around Y axis
            angle = np.arctan2(vertex[0], vertex[2])
            u = (angle + np.pi) / (2 * np.pi)

            # Use Y coordinate for V
            v = (vertex[1] + 1.0) / 2.0  # Normalize to 0-1

            uv_coords.append([u, v])

        return np.array(uv_coords)

    def _generate_planar_uv(self, mesh: trimesh.Trimesh) -> np.ndarray:
        """Generate planar UV mapping"""
        vertices = mesh.vertices
        uv_coords = []

        # Find bounds
        min_coords = np.min(vertices, axis=0)
        max_coords = np.max(vertices, axis=0)

        for vertex in vertices:
            # Map X and Z to U and V
            u = (vertex[0] - min_coords[0]) / (max_coords[0] - min_coords[0]) if max_coords[0] != min_coords[0] else 0.0
            v = (vertex[2] - min_coords[2]) / (max_coords[2] - min_coords[2]) if max_coords[2] != min_coords[2] else 0.0

            uv_coords.append([u, v])

        return np.array(uv_coords)

    def _generate_procedural_uv(self, mesh: trimesh.Trimesh) -> np.ndarray:
        """Generate procedural UV mapping based on vertex properties"""
        vertices = mesh.vertices
        uv_coords = []

        for vertex in vertices:
            # Use vertex position and normal to create unique UV
            # This creates a more organic texture mapping
            x, y, z = vertex

            # Combine position and some noise for UV
            u = (x * 0.3 + y * 0.7 + np.random.random() * 0.1) % 1.0
            v = (z * 0.4 + y * 0.5 + np.random.random() * 0.1) % 1.0

            uv_coords.append([u, v])

        return np.array(uv_coords)

    def create_material_file(self, material: Dict, filename: str) -> str:
        """
        Create a .mtl file for the material

        Args:
            material: Material properties dictionary
            filename: Output filename

        Returns:
            Path to created material file
        """
        mtl_content = f"""# Material file generated by ModelForge
newmtl {filename}

Ka {material['diffuse'][0]*0.3} {material['diffuse'][1]*0.3} {material['diffuse'][2]*0.3}
Kd {material['diffuse'][0]} {material['diffuse'][1]} {material['diffuse'][2]}
Ks {material['specular'][0]} {material['specular'][1]} {material['specular'][2]}
Ns {1000 * (1 - material['roughness'])}

"""

        # Add transparency if present
        if 'alpha' in material:
            mtl_content += f"d {material['alpha']}\n"

        # Add illumination model
        if material['metallic'] > 0.5:
            mtl_content += "illum 3\n"  # Metal
        else:
            mtl_content += "illum 2\n"  # Diffuse + specular

        # Write to file
        filepath = f"generated/{filename}.mtl"
        os.makedirs("generated", exist_ok=True)

        with open(filepath, 'w') as f:
            f.write(mtl_content)

        return filepath

    def apply_material_to_mesh(self, mesh: trimesh.Trimesh, material: Dict) -> trimesh.Trimesh:
        """
        Apply material properties to mesh by modifying vertex colors

        Args:
            mesh: Input mesh
            material: Material properties

        Returns:
            Mesh with applied material colors
        """
        # Create vertex colors based on material
        vertex_colors = []

        for vertex in mesh.vertices:
            # Base color from material
            base_color = material['diffuse']

            # Add some variation based on vertex position
            variation = (vertex[0] * 0.1 + vertex[1] * 0.1 + vertex[2] * 0.1) % 0.2

            color = [
                max(0.0, min(1.0, base_color[0] + variation - 0.1)),
                max(0.0, min(1.0, base_color[1] + variation - 0.1)),
                max(0.0, min(1.0, base_color[2] + variation - 0.1)),
                1.0  # Alpha
            ]

            vertex_colors.append(color)

        # Apply vertex colors to mesh
        mesh.visual.vertex_colors = vertex_colors

        return mesh

    def generate_texture_image(self, material: Dict, size: Tuple[int, int] = (512, 512)) -> str:
        """
        Generate a procedural texture image for the material

        Args:
            material: Material properties
            size: Texture size

        Returns:
            Path to generated texture file
        """
        width, height = size

        # Create texture based on material type
        if material.get('metallic', 0) > 0.5:
            texture_array = self._generate_metal_texture(width, height, material)
        elif 'wood' in str(material):
            texture_array = self._generate_wood_texture(width, height, material)
        elif 'stone' in str(material):
            texture_array = self._generate_stone_texture(width, height, material)
        else:
            texture_array = self._generate_generic_texture(width, height, material)

        # Convert to PIL Image and save
        try:
            from PIL import Image
            texture_image = Image.fromarray((texture_array * 255).astype(np.uint8))

            # Generate filename
            import hashlib
            material_hash = hashlib.md5(str(material).encode()).hexdigest()[:8]
            texture_filename = f"texture_{material_hash}.png"
            texture_path = f"generated/{texture_filename}"

            os.makedirs("generated", exist_ok=True)
            texture_image.save(texture_path)

            return texture_path

        except ImportError:
            logging.warning("PIL not available, cannot generate texture image")
            return ""

    def _generate_metal_texture(self, width: int, height: int, material: Dict) -> np.ndarray:
        """Generate metallic texture"""
        texture = np.zeros((height, width, 3))

        # Create brushed metal effect
        for y in range(height):
            for x in range(width):
                # Base color
                base_color = material['diffuse']

                # Add noise for texture
                noise = (np.random.random() - 0.5) * 0.1

                # Add horizontal brushing effect
                brush_effect = np.sin(y * 0.1) * 0.05

                color = [
                    max(0.0, min(1.0, base_color[0] + noise + brush_effect)),
                    max(0.0, min(1.0, base_color[1] + noise + brush_effect)),
                    max(0.0, min(1.0, base_color[2] + noise + brush_effect))
                ]

                texture[y, x] = color

        return texture

    def _generate_wood_texture(self, width: int, height: int, material: Dict) -> np.ndarray:
        """Generate wood grain texture"""
        texture = np.zeros((height, width, 3))

        # Create wood grain pattern
        for y in range(height):
            for x in range(width):
                # Wood grain rings
                ring_effect = np.sin(np.sqrt((x - width/2)**2 + (y - height/2)**2) * 0.02) * 0.1

                # Wood grain lines
                grain_effect = np.sin(y * 0.05) * 0.05

                # Base wood color
                base_color = material['diffuse']

                color = [
                    max(0.0, min(1.0, base_color[0] + ring_effect + grain_effect)),
                    max(0.0, min(1.0, base_color[1] + ring_effect + grain_effect * 0.8)),
                    max(0.0, min(1.0, base_color[2] + ring_effect + grain_effect * 0.6))
                ]

                texture[y, x] = color

        return texture

    def _generate_stone_texture(self, width: int, height: int, material: Dict) -> np.ndarray:
        """Generate stone texture"""
        texture = np.zeros((height, width, 3))

        # Create mottled stone effect
        for y in range(height):
            for x in range(width):
                # Multiple octaves of noise for stone texture
                noise1 = np.random.random() * 0.1
                noise2 = np.sin(x * 0.03) * np.cos(y * 0.03) * 0.05

                base_color = material['diffuse']

                color = [
                    max(0.0, min(1.0, base_color[0] + noise1 + noise2)),
                    max(0.0, min(1.0, base_color[1] + noise1 + noise2)),
                    max(0.0, min(1.0, base_color[2] + noise1 + noise2))
                ]

                texture[y, x] = color

        return texture

    def _generate_generic_texture(self, width: int, height: int, material: Dict) -> np.ndarray:
        """Generate generic procedural texture"""
        texture = np.zeros((height, width, 3))

        # Simple noise-based texture
        for y in range(height):
            for x in range(width):
                noise = (np.random.random() - 0.5) * 0.2

                base_color = material['diffuse']

                color = [
                    max(0.0, min(1.0, base_color[0] + noise)),
                    max(0.0, min(1.0, base_color[1] + noise)),
                    max(0.0, min(1.0, base_color[2] + noise))
                ]

                texture[y, x] = color

        return texture


def create_material_generator() -> MaterialGenerator:
    """Factory function to create material generator"""
    return MaterialGenerator()


# Standalone functions for backward compatibility
def generate_material_for_mesh(mesh: trimesh.Trimesh, prompt: str, style: str = "realistic") -> trimesh.Trimesh:
    """Generate and apply material to mesh"""
    generator = MaterialGenerator()
    material = generator.generate_material_for_prompt(prompt, style)
    return generator.apply_material_to_mesh(mesh, material)


def create_texture_for_material(material: Dict, size: Tuple[int, int] = (512, 512)) -> str:
    """Create texture image for material"""
    generator = MaterialGenerator()
    return generator.generate_texture_image(material, size)