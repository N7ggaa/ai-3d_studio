import os
import logging
import numpy as np
import trimesh
import math
import time
import hashlib
from typing import Dict, Any, Optional

# Import advanced generation modules (optional)
USE_ADVANCED = True
try:
    from instance.ai_modules.advanced_generator import AdvancedModelGenerator, GenerationConfig, GenerationEngine
    from instance.ai_modules.ai_integration import AIServiceManager, AIService
    from instance.ai_modules.multimodal_processor import create_multimodal_processor, MultimodalConfig, ModalityEngine
    from instance.ai_modules.export_engine import create_export_engine, ExportFormat, OptimizationConfig
    from instance.ai_modules.material_generator import MaterialGenerator, create_material_generator
except Exception as e:
    logging.warning(f"Advanced AI modules not available, falling back to procedural only: {e}")
    USE_ADVANCED = False

# Set up basic logging
logging.basicConfig(level=logging.INFO)

# Initialize advanced generators (if available)
advanced_generator = AdvancedModelGenerator() if USE_ADVANCED else None
ai_service_manager = AIServiceManager() if USE_ADVANCED else None

# Initialize multimodal processor
multimodal_processor = create_multimodal_processor(MultimodalConfig(engine=ModalityEngine.CLIP)) if USE_ADVANCED else None

# Initialize export engine (if available)
export_engine = create_export_engine(OptimizationConfig(
    target_poly_count=5000,
    optimize_for_game_engine="roblox"
)) if USE_ADVANCED else None

# Initialize material generator (if available)
material_generator = create_material_generator() if USE_ADVANCED else None

def generate_3d_model(prompt, reference_image_path=None, job_id=None, engine="hybrid", complexity=7, detail_level=8, material_style="realistic"):
    """
    Generate a 3D model from text prompt and optional reference image
    Uses advanced AI-powered generation with multiple engines and comprehensive error handling

    Args:
        prompt (str): Text description of the 3D model
        reference_image_path (str, optional): Path to reference image
        job_id (int, optional): Job ID for file naming
        engine (str): Generation engine ("procedural", "ai_enhanced", "hybrid", "texture_generated")
        complexity (int): Model complexity (1-10)
        detail_level (int): Detail level (1-10)
        material_style (str): Material style ("realistic", "stylized", "low_poly", "sci_fi", "fantasy")

    Returns:
        str: Path to generated .obj file
    """
    # Input validation and sanitization
    if not prompt or not isinstance(prompt, str) or len(prompt.strip()) == 0:
        raise ValueError("Prompt cannot be empty")

    prompt = prompt.strip()[:500]  # Limit prompt length

    # Validate parameters
    complexity = max(1, min(10, complexity))
    detail_level = max(1, min(10, detail_level))

    # Validate material style
    valid_styles = ["realistic", "stylized", "low_poly", "sci_fi", "fantasy", "cartoon"]
    if material_style not in valid_styles:
        logging.warning(f"Invalid material style '{material_style}', using 'realistic'")
        material_style = "realistic"

    # Validate engine
    valid_engines = ["procedural", "ai_enhanced", "hybrid", "texture_generated"]
    if engine not in valid_engines:
        logging.warning(f"Invalid engine '{engine}', using 'hybrid'")
        engine = "hybrid"

    try:
        logging.info(f"Generating 3D model for prompt: {prompt}")
        logging.info(f"Using engine: {engine}, complexity: {complexity}, detail_level: {detail_level}")
        
        # Process multimodal input if both text and image are provided (only if advanced available)
        enhanced_prompt = prompt
        if USE_ADVANCED and reference_image_path and os.path.exists(reference_image_path):
            logging.info("Processing multimodal input (text + image)")
            try:
                if multimodal_processor:
                    multimodal_result = multimodal_processor.process_text_and_image(prompt, reference_image_path)
                    if multimodal_result and multimodal_result.get('success'):
                        enhanced_prompt = multimodal_result.get('enhanced_prompt', prompt)
                        logging.info(f"Enhanced prompt: {enhanced_prompt}")
                    else:
                        logging.warning(f"Multimodal processing failed: {multimodal_result.get('error', 'Unknown error') if multimodal_result else 'No result'}")
                else:
                    logging.warning("Multimodal processor not available")
            except Exception as e:
                logging.warning(f"Error in multimodal processing: {e}")
                enhanced_prompt = prompt  # Fallback to original prompt
        
        # Determine generation approach with comprehensive error handling
        mesh = None

        if USE_ADVANCED and engine == "ai_enhanced" and ai_service_manager and ai_service_manager.get_available_services():
            # Try AI-powered generation first
            logging.info("Attempting AI-powered generation")
            try:
                if ai_service_manager:
                    ai_result = ai_service_manager.generate_with_best_service(enhanced_prompt, reference_image_path)

                    if ai_result and ai_result.get('success'):
                        mesh = ai_result.get('mesh')
                        if mesh:
                            logging.info(f"AI generation successful using {ai_result.get('service', 'unknown')} service")
                        else:
                            logging.warning("AI generation returned success but no mesh")
                    else:
                        logging.warning(f"AI generation failed: {ai_result.get('error', 'Unknown error') if ai_result else 'No result'}")
                else:
                    logging.warning("AI service manager not available")
            except Exception as e:
                logging.error(f"Error in AI generation: {e}")
        else:
            logging.info("AI generation not available or not requested, using procedural generation")
        
        # Fallback generation with comprehensive error handling
        if mesh is None:
            try:
                if USE_ADVANCED and advanced_generator is not None:
                    logging.info("Using advanced procedural generation")
                    try:
                        # Create generation configuration with error handling
                        config = GenerationConfig(
                            engine=GenerationEngine(engine),
                            complexity=complexity,
                            detail_level=detail_level,
                            material_style=material_style,
                            generate_textures=True,
                            generate_materials=True,
                            variations=1,
                            seed=int(time.time()) if job_id else None
                        )
                        # Generate using advanced generator
                        result = advanced_generator.generate_model(prompt, config, reference_image_path)
                        if result and 'mesh' in result:
                            mesh = result['mesh']
                            # Log generation metadata
                            metadata = result.get('metadata', {})
                            logging.info(f"Generated mesh: {metadata.get('vertex_count', 0)} vertices, {metadata.get('face_count', 0)} faces")
                        else:
                            logging.warning("Advanced generator returned no mesh")
                            mesh = None
                    except Exception as e:
                        logging.error(f"Error in advanced generator: {e}")
                        mesh = None
                else:
                    logging.info("Using basic procedural generation fallback")
                    mesh = generate_geometry_from_prompt(prompt)
            except Exception as e:
                logging.error(f"Error in fallback generation: {e}")
                # Last resort fallback
                mesh = create_default_mesh()
        
        if mesh is None:
            raise Exception("Failed to generate 3D geometry")

        # Apply material and texture if material generator is available
        if USE_ADVANCED and material_generator is not None and mesh is not None:
            try:
                # Generate material based on prompt and style
                material = material_generator.generate_material_for_prompt(prompt, material_style)

                # Apply material to mesh
                mesh = material_generator.apply_material_to_mesh(mesh, material)

                # Generate texture if requested (optional, don't fail if this fails)
                try:
                    texture_path = material_generator.generate_texture_image(material)
                    if texture_path:
                        logging.info(f"Generated texture: {texture_path}")
                except Exception as e:
                    logging.warning(f"Texture generation failed: {e}")
                    texture_path = None

                # Create material file
                material_filename = f"model_{job_id}_material" if job_id else f"model_{hash(prompt)}_material"
                mtl_path = material_generator.create_material_file(material, material_filename)
                logging.info(f"Created material file: {mtl_path}")

            except Exception as e:
                logging.warning(f"Material generation failed, using default mesh: {e}")

        # Save as OBJ file with comprehensive error handling
        if mesh is None:
            raise ValueError("No mesh generated to save")

        output_filename = f"model_{job_id}.obj" if job_id else f"model_{hash(prompt)}.obj"
        output_path = os.path.join("generated", output_filename)

        # Ensure directory exists
        try:
            os.makedirs("generated", exist_ok=True)
        except Exception as e:
            logging.error(f"Failed to create output directory: {e}")
            # Try alternative location
            output_path = output_filename

        # Export with multiple fallback mechanisms
        export_success = False

        if USE_ADVANCED and export_engine is not None:
            try:
                # Export using export engine for optimization
                success = export_engine.export_model(mesh, ExportFormat.OBJ, output_path)
                if success:
                    export_success = True
                    logging.info(f"Successfully exported using export engine: {output_path}")
                else:
                    logging.warning("Export engine failed, falling back to direct export")
            except Exception as e:
                logging.error(f"Export engine error: {e}")

        # Fallback to direct export
        if not export_success:
            try:
                mesh.export(output_path)
                export_success = True
                logging.info(f"Successfully exported using direct method: {output_path}")
            except Exception as e:
                logging.error(f"Direct export failed: {e}")
                # Try alternative formats
                try:
                    # Try STL format as last resort
                    stl_path = output_path.replace('.obj', '.stl')
                    mesh.export(stl_path)
                    output_path = stl_path
                    export_success = True
                    logging.warning(f"OBJ export failed, saved as STL: {output_path}")
                except Exception as e2:
                    logging.error(f"STL export also failed: {e2}")
                    raise Exception(f"All export methods failed. OBJ: {e}, STL: {e2}")

        if not export_success:
            raise Exception("Failed to export mesh in any format")

        logging.info(f"3D model saved to: {output_path}")
        return output_path
        
    except Exception as e:
        logging.error(f"Error in generate_3d_model: {str(e)}")
        # Provide detailed error information for debugging
        error_details = {
            'error': str(e),
            'prompt': prompt[:100] + '...' if len(prompt) > 100 else prompt,
            'engine': engine,
            'complexity': complexity,
            'detail_level': detail_level,
            'material_style': material_style,
            'has_reference_image': reference_image_path is not None,
            'advanced_available': USE_ADVANCED,
            'timestamp': time.time()
        }
        logging.error(f"Generation error details: {error_details}")
        raise Exception(f"3D model generation failed: {str(e)}")

def generate_geometry_from_prompt(prompt):
    """
    Generate enhanced 3D geometry based on text prompt keywords with improved algorithms

    Args:
        prompt (str): Text description

    Returns:
        trimesh.Trimesh: Generated mesh
    """
    prompt_lower = prompt.lower()

    try:
        # Enhanced shape detection with more sophisticated algorithms
        if any(word in prompt_lower for word in ['spaceship', 'rocket', 'ship', 'spacecraft']):
            return create_enhanced_spaceship_mesh(prompt)
        elif any(word in prompt_lower for word in ['car', 'vehicle', 'automobile', 'truck']):
            return create_enhanced_car_mesh(prompt)
        elif any(word in prompt_lower for word in ['chair', 'seat', 'furniture']):
            return create_enhanced_chair_mesh(prompt)
        elif any(word in prompt_lower for word in ['castle', 'tower', 'building', 'structure']):
            return create_enhanced_building_mesh(prompt)
        elif any(word in prompt_lower for word in ['sphere', 'ball', 'orb', 'globe']):
            return create_enhanced_sphere_mesh(prompt)
        elif any(word in prompt_lower for word in ['cube', 'box', 'block', 'die']):
            return create_enhanced_cube_mesh(prompt)
        elif any(word in prompt_lower for word in ['cylinder', 'tube', 'pipe', 'column']):
            return create_enhanced_cylinder_mesh(prompt)
        elif any(word in prompt_lower for word in ['human', 'person', 'character', 'humanoid']):
            return create_humanoid_mesh(prompt)
        elif any(word in prompt_lower for word in ['animal', 'creature', 'beast']):
            return create_creature_mesh(prompt)
        elif any(word in prompt_lower for word in ['weapon', 'sword', 'gun', 'blade']):
            return create_weapon_mesh(prompt)
        elif any(word in prompt_lower for word in ['plant', 'tree', 'flower']):
            return create_plant_mesh(prompt)
        elif any(word in prompt_lower for word in ['robot', 'mech', 'android', 'machine']):
            return create_robot_mesh(prompt)
        else:
            # Use advanced procedural generation for unknown objects
            return create_procedural_mesh(prompt)

    except Exception as e:
        logging.warning(f"Error creating specific geometry, using default: {e}")
        return create_default_mesh()

def create_spaceship_mesh():
    """Create a basic spaceship-like mesh"""
    # Main body (elongated ellipsoid)
    main_body = trimesh.creation.capsule(radius=0.5, height=3.0)
    
    # Wings (flattened boxes)
    wing1 = trimesh.creation.box(extents=[2.0, 0.2, 0.5])
    wing1.apply_translation([0, 0, 0.5])
    
    wing2 = trimesh.creation.box(extents=[2.0, 0.2, 0.5])
    wing2.apply_translation([0, 0, -0.5])
    
    # Combine meshes
    spaceship = trimesh.util.concatenate([main_body, wing1, wing2])
    return spaceship

def create_car_mesh():
    """Create a basic car-like mesh"""
    # Main body
    body = trimesh.creation.box(extents=[3.0, 1.5, 0.8])
    body.apply_translation([0, 0, 0.5])
    
    # Cabin
    cabin = trimesh.creation.box(extents=[1.5, 1.2, 0.6])
    cabin.apply_translation([0, 0, 1.2])
    
    # Wheels
    wheel_positions = [
        [1.0, 0.6, 0],
        [1.0, -0.6, 0],
        [-1.0, 0.6, 0],
        [-1.0, -0.6, 0]
    ]
    
    wheels = []
    for pos in wheel_positions:
        wheel = trimesh.creation.cylinder(radius=0.3, height=0.2)
        wheel.apply_translation(pos)
        wheels.append(wheel)
    
    # Combine all parts
    car_parts = [body, cabin] + wheels
    car = trimesh.util.concatenate(car_parts)
    return car

def create_chair_mesh():
    """Create a basic chair mesh"""
    # Seat
    seat = trimesh.creation.box(extents=[1.0, 1.0, 0.1])
    seat.apply_translation([0, 0, 0.8])
    
    # Backrest
    backrest = trimesh.creation.box(extents=[1.0, 0.1, 1.0])
    backrest.apply_translation([0, 0.45, 1.3])
    
    # Legs
    leg_positions = [
        [0.4, 0.4, 0.4],
        [0.4, -0.4, 0.4],
        [-0.4, 0.4, 0.4],
        [-0.4, -0.4, 0.4]
    ]
    
    legs = []
    for pos in leg_positions:
        leg = trimesh.creation.cylinder(radius=0.05, height=0.8)
        leg.apply_translation(pos)
        legs.append(leg)
    
    # Combine all parts
    chair_parts = [seat, backrest] + legs
    chair = trimesh.util.concatenate(chair_parts)
    return chair

def create_tower_mesh():
    """Create a basic tower/castle mesh"""
    # Main tower
    tower = trimesh.creation.cylinder(radius=1.0, height=4.0)
    tower.apply_translation([0, 0, 2.0])
    
    # Cone roof
    roof = trimesh.creation.cone(radius=1.2, height=1.5)
    roof.apply_translation([0, 0, 4.75])
    
    # Base
    base = trimesh.creation.cylinder(radius=1.5, height=0.5)
    base.apply_translation([0, 0, 0.25])
    
    # Combine parts
    castle = trimesh.util.concatenate([base, tower, roof])
    return castle

def create_default_mesh():
    """Create a default interesting mesh when no specific shape is detected"""
    # Create a more complex default mesh using procedural generation
    return create_procedural_mesh("abstract geometric shape")


def create_enhanced_spaceship_mesh(prompt):
    """Create an enhanced spaceship with more detail and procedural variations"""
    # Main hull - elongated capsule
    hull = trimesh.creation.capsule(radius=0.8, height=4.0)

    # Wings with procedural variation
    wing1 = trimesh.creation.box(extents=[3.0, 0.3, 1.5])
    wing1.apply_translation([0, 0, 0.8])
    wing2 = trimesh.creation.box(extents=[3.0, 0.3, 1.5])
    wing2.apply_translation([0, 0, -0.8])

    # Engine pods
    engine1 = trimesh.creation.cylinder(radius=0.3, height=1.2)
    engine1.apply_translation([0, -2.2, 0.5])
    engine2 = trimesh.creation.cylinder(radius=0.3, height=1.2)
    engine2.apply_translation([0, -2.2, -0.5])

    # Cockpit
    cockpit = trimesh.creation.uv_sphere(radius=0.6)
    cockpit.apply_translation([1.5, 0, 0])

    # Combine all parts
    spaceship_parts = [hull, wing1, wing2, engine1, engine2, cockpit]
    spaceship = trimesh.util.concatenate(spaceship_parts)

    # Add some procedural surface detail
    spaceship = add_surface_detail(spaceship, "metallic")

    return spaceship


def create_enhanced_car_mesh(prompt):
    """Create an enhanced car with more realistic proportions"""
    # Main body with better proportions
    body = trimesh.creation.box(extents=[4.0, 2.0, 1.2])
    body.apply_translation([0, 0, 0.6])

    # Cabin with windshield angle
    cabin = trimesh.creation.box(extents=[2.0, 1.8, 1.0])
    cabin.apply_translation([0, 0, 1.5])

    # Wheels with proper positioning
    wheel_positions = [
        [1.5, 1.0, 0],
        [1.5, -1.0, 0],
        [-1.5, 1.0, 0],
        [-1.5, -1.0, 0]
    ]

    wheels = []
    for pos in wheel_positions:
        wheel = trimesh.creation.cylinder(radius=0.4, height=0.3)
        wheel.apply_translation(pos)
        wheels.append(wheel)

    # Add wheel wells
    wheel_well1 = trimesh.creation.box(extents=[0.8, 0.6, 0.8])
    wheel_well1.apply_translation([1.5, 1.0, 0.3])
    wheel_well2 = trimesh.creation.box(extents=[0.8, 0.6, 0.8])
    wheel_well2.apply_translation([1.5, -1.0, 0.3])
    wheel_well3 = trimesh.creation.box(extents=[0.8, 0.6, 0.8])
    wheel_well3.apply_translation([-1.5, 1.0, 0.3])
    wheel_well4 = trimesh.creation.box(extents=[0.8, 0.6, 0.8])
    wheel_well4.apply_translation([-1.5, -1.0, 0.3])

    # Combine all parts
    car_parts = [body, cabin, wheel_well1, wheel_well2, wheel_well3, wheel_well4] + wheels
    car = trimesh.util.concatenate(car_parts)

    return car


def create_enhanced_chair_mesh(prompt):
    """Create an enhanced chair with more detail"""
    # Seat cushion
    seat = trimesh.creation.box(extents=[1.2, 1.2, 0.15])
    seat.apply_translation([0, 0, 0.9])

    # Backrest with curve
    backrest = trimesh.creation.box(extents=[1.2, 0.15, 1.4])
    backrest.apply_translation([0, 0.55, 1.6])

    # Chair legs
    leg_positions = [
        [0.5, 0.5, 0.45],
        [0.5, -0.5, 0.45],
        [-0.5, 0.5, 0.45],
        [-0.5, -0.5, 0.45]
    ]

    legs = []
    for pos in leg_positions:
        leg = trimesh.creation.cylinder(radius=0.08, height=0.9)
        leg.apply_translation(pos)
        legs.append(leg)

    # Armrests
    armrest1 = trimesh.creation.box(extents=[0.15, 0.8, 0.15])
    armrest1.apply_translation([0.65, 0, 1.3])
    armrest2 = trimesh.creation.box(extents=[0.15, 0.8, 0.15])
    armrest2.apply_translation([-0.65, 0, 1.3])

    # Combine all parts
    chair_parts = [seat, backrest, armrest1, armrest2] + legs
    chair = trimesh.util.concatenate(chair_parts)

    return chair


def create_enhanced_building_mesh(prompt):
    """Create an enhanced building with procedural variations"""
    # Main structure with variable height
    height = 5.0 + np.random.random() * 3.0
    building = trimesh.creation.box(extents=[3.0, 3.0, height])
    building.apply_translation([0, 0, height/2])

    # Roof with different styles
    if 'tower' in prompt.lower():
        roof = trimesh.creation.cone(radius=1.8, height=2.0)
        roof.apply_translation([0, 0, height + 1.0])
    else:
        roof = trimesh.creation.box(extents=[3.2, 3.2, 0.5])
        roof.apply_translation([0, 0, height + 0.25])

    # Add windows procedurally
    windows = []
    for floor in range(int(height // 1.5)):
        for side in range(4):  # Four sides
            window = trimesh.creation.box(extents=[0.6, 0.1, 0.8])
            # Position windows on each side
            if side == 0:  # Front
                window.apply_translation([0, 1.6, 0.8 + floor * 1.5])
            elif side == 1:  # Back
                window.apply_translation([0, -1.6, 0.8 + floor * 1.5])
            elif side == 2:  # Right
                window.apply_translation([1.6, 0, 0.8 + floor * 1.5])
                window.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2, [0, 0, 1]))
            else:  # Left
                window.apply_translation([-1.6, 0, 0.8 + floor * 1.5])
                window.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2, [0, 0, 1]))
            windows.append(window)

    # Combine all parts
    building_parts = [building, roof] + windows
    complete_building = trimesh.util.concatenate(building_parts)

    return complete_building


def create_enhanced_sphere_mesh(prompt):
    """Create an enhanced sphere with surface modifications"""
    # Base sphere
    sphere = trimesh.creation.uv_sphere(radius=1.2)

    # Add some surface variation if requested
    if 'spiked' in prompt.lower() or 'textured' in prompt.lower():
        sphere = add_spherical_detail(sphere)

    return sphere


def create_enhanced_cube_mesh(prompt):
    """Create an enhanced cube with beveled edges or other modifications"""
    # Base cube
    cube = trimesh.creation.box(extents=[2.0, 2.0, 2.0])

    # Add beveling if requested
    if 'rounded' in prompt.lower() or 'smooth' in prompt.lower():
        cube = add_beveled_edges(cube)

    return cube


def create_enhanced_cylinder_mesh(prompt):
    """Create an enhanced cylinder with variations"""
    # Base cylinder
    cylinder = trimesh.creation.cylinder(radius=0.8, height=2.5)

    # Add variations based on prompt
    if 'fluted' in prompt.lower():
        cylinder = add_fluted_detail(cylinder)
    elif 'twisted' in prompt.lower():
        cylinder = add_twist_detail(cylinder)

    return cylinder


def create_humanoid_mesh(prompt):
    """Create a basic humanoid figure"""
    # Torso
    torso = trimesh.creation.capsule(radius=0.6, height=1.5)

    # Head
    head = trimesh.creation.uv_sphere(radius=0.4)
    head.apply_translation([0, 0, 1.2])

    # Arms
    arm1 = trimesh.creation.capsule(radius=0.2, height=1.2)
    arm1.apply_translation([-0.8, 0, 0.3])
    arm2 = trimesh.creation.capsule(radius=0.2, height=1.2)
    arm2.apply_translation([0.8, 0, 0.3])

    # Legs
    leg1 = trimesh.creation.capsule(radius=0.25, height=1.5)
    leg1.apply_translation([-0.3, 0, -1.0])
    leg2 = trimesh.creation.capsule(radius=0.25, height=1.5)
    leg2.apply_translation([0.3, 0, -1.0])

    # Combine parts
    humanoid_parts = [torso, head, arm1, arm2, leg1, leg2]
    humanoid = trimesh.util.concatenate(humanoid_parts)

    return humanoid


def create_creature_mesh(prompt):
    """Create a creature based on prompt keywords"""
    # Base body
    body = trimesh.creation.uv_sphere(radius=1.0)

    # Add creature-specific features
    if 'tentacles' in prompt.lower():
        tentacles = create_tentacle_array(6)
        body = trimesh.util.concatenate([body] + tentacles)
    elif 'wings' in prompt.lower():
        wings = create_wing_pair()
        body = trimesh.util.concatenate([body] + wings)
    elif 'horns' in prompt.lower():
        horns = create_horn_pair()
        body = trimesh.util.concatenate([body] + horns)

    return body


def create_weapon_mesh(prompt):
    """Create a weapon based on type"""
    if 'sword' in prompt.lower():
        return create_sword_mesh()
    elif 'gun' in prompt.lower():
        return create_gun_mesh()
    else:
        return create_generic_weapon_mesh()


def create_plant_mesh(prompt):
    """Create a plant-like structure"""
    # Main stem
    stem = trimesh.creation.cylinder(radius=0.1, height=3.0)

    # Leaves or flowers
    leaves = []
    for i in range(5):
        leaf = trimesh.creation.box(extents=[0.8, 0.3, 0.05])
        leaf.apply_translation([0, 0, 0.5 + i * 0.5])
        leaf.apply_transform(trimesh.transformations.rotation_matrix(np.pi/4 * i, [0, 0, 1]))
        leaves.append(leaf)

    # Combine
    plant_parts = [stem] + leaves
    plant = trimesh.util.concatenate(plant_parts)

    return plant


def create_robot_mesh(prompt):
    """Create a robotic figure"""
    # Main body
    body = trimesh.creation.box(extents=[1.5, 1.0, 2.0])

    # Head
    head = trimesh.creation.box(extents=[0.8, 0.8, 0.8])
    head.apply_translation([0, 0, 1.5])

    # Arms with joints
    arm1 = trimesh.creation.cylinder(radius=0.2, height=1.0)
    arm1.apply_translation([-1.0, 0, 0.5])
    arm2 = trimesh.creation.cylinder(radius=0.2, height=1.0)
    arm2.apply_translation([1.0, 0, 0.5])

    # Legs
    leg1 = trimesh.creation.box(extents=[0.3, 0.3, 1.2])
    leg1.apply_translation([-0.4, 0, -0.8])
    leg2 = trimesh.creation.box(extents=[0.3, 0.3, 1.2])
    leg2.apply_translation([0.4, 0, -0.8])

    # Combine
    robot_parts = [body, head, arm1, arm2, leg1, leg2]
    robot = trimesh.util.concatenate(robot_parts)

    return robot


def create_procedural_mesh(prompt):
    """Create a mesh using advanced procedural generation techniques"""
    # Use noise and mathematical functions to create organic shapes
    vertices = []
    faces = []

    # Create a base shape using parametric equations
    for i in range(32):
        for j in range(16):
            theta = (i / 32.0) * 2 * np.pi
            phi = (j / 16.0) * np.pi

            # Use noise to create organic variation
            noise_factor = (np.random.random() - 0.5) * 0.3

            x = (1 + noise_factor) * np.sin(phi) * np.cos(theta)
            y = (1 + noise_factor) * np.sin(phi) * np.sin(theta)
            z = (1 + noise_factor) * np.cos(phi)

            vertices.append([x, y, z])

    # Generate faces
    for i in range(31):
        for j in range(15):
            v1 = i * 16 + j
            v2 = ((i + 1) % 32) * 16 + j
            v3 = ((i + 1) % 32) * 16 + (j + 1) % 16
            v4 = i * 16 + (j + 1) % 16

            faces.append([v1, v2, v3])
            faces.append([v1, v3, v4])

    # Create mesh
    procedural_mesh = trimesh.Trimesh(vertices=vertices, faces=faces)

    # Apply transformations based on prompt
    if 'twisted' in prompt.lower():
        procedural_mesh = add_twist_detail(procedural_mesh)
    elif 'spiked' in prompt.lower():
        procedural_mesh = add_spike_detail(procedural_mesh)

    return procedural_mesh


def add_surface_detail(mesh, material_type="generic"):
    """Add surface detail to a mesh based on material type"""
    # This is a placeholder for more advanced surface detail generation
    # In a full implementation, this would add procedural textures, bumps, etc.

    if material_type == "metallic":
        # Add some geometric surface patterns
        return mesh
    elif material_type == "organic":
        # Add organic surface patterns
        return mesh
    else:
        return mesh


def add_spherical_detail(sphere):
    """Add detail to spherical objects"""
    # Placeholder for adding spikes or texture to spheres
    return sphere


def add_beveled_edges(cube):
    """Add beveled edges to cube"""
    # Placeholder for beveling operation
    return cube


def add_fluted_detail(cylinder):
    """Add fluted detail to cylinder"""
    # Placeholder for adding flutes
    return cylinder


def add_twist_detail(mesh):
    """Add twist deformation to mesh"""
    # Apply twist transformation
    vertices = mesh.vertices
    center = np.mean(vertices, axis=0)

    # Twist vertices around Z axis
    for i, vertex in enumerate(vertices):
        # Calculate angle based on Z coordinate
        z_normalized = (vertex[2] - center[2]) / 2.0
        angle = z_normalized * np.pi / 2  # Half twist

        # Rotate around center
        x = vertex[0] - center[0]
        y = vertex[1] - center[1]

        cos_angle = np.cos(angle)
        sin_angle = np.sin(angle)

        new_x = x * cos_angle - y * sin_angle
        new_y = x * sin_angle + y * cos_angle

        vertices[i] = [new_x + center[0], new_y + center[1], vertex[2]]

    return trimesh.Trimesh(vertices=vertices, faces=mesh.faces)


def create_tentacle_array(count):
    """Create array of tentacles"""
    tentacles = []
    for i in range(count):
        tentacle = trimesh.creation.capsule(radius=0.1, height=2.0)
        angle = (i / count) * 2 * np.pi
        tentacle.apply_translation([np.cos(angle), np.sin(angle), 0])
        tentacles.append(tentacle)
    return tentacles


def create_wing_pair():
    """Create pair of wings"""
    wing1 = trimesh.creation.box(extents=[2.0, 0.1, 1.0])
    wing1.apply_translation([1.0, 0, 0])
    wing2 = trimesh.creation.box(extents=[2.0, 0.1, 1.0])
    wing2.apply_translation([-1.0, 0, 0])
    return [wing1, wing2]


def create_horn_pair():
    """Create pair of horns"""
    horn1 = trimesh.creation.cone(radius=0.2, height=0.8)
    horn1.apply_translation([0.3, 0.3, 0.8])
    horn2 = trimesh.creation.cone(radius=0.2, height=0.8)
    horn2.apply_translation([-0.3, 0.3, 0.8])
    return [horn1, horn2]


def create_sword_mesh():
    """Create a sword mesh"""
    # Blade
    blade = trimesh.creation.box(extents=[0.1, 2.0, 0.02])
    blade.apply_translation([0, 1.0, 0])

    # Hilt
    hilt = trimesh.creation.cylinder(radius=0.05, height=0.3)
    hilt.apply_translation([0, 0, 0])

    # Guard
    guard = trimesh.creation.box(extents=[0.3, 0.05, 0.1])
    guard.apply_translation([0, 0.15, 0])

    # Pommel
    pommel = trimesh.creation.uv_sphere(radius=0.08)
    pommel.apply_translation([0, -0.15, 0])

    sword_parts = [blade, hilt, guard, pommel]
    sword = trimesh.util.concatenate(sword_parts)

    return sword


def create_gun_mesh():
    """Create a gun mesh"""
    # Main body
    body = trimesh.creation.box(extents=[0.8, 0.3, 0.2])
    body.apply_translation([0, 0, 0.1])

    # Barrel
    barrel = trimesh.creation.cylinder(radius=0.08, height=1.0)
    barrel.apply_translation([0.5, 0, 0.1])

    # Handle
    handle = trimesh.creation.box(extents=[0.15, 0.4, 0.2])
    handle.apply_translation([-0.3, 0, -0.1])

    gun_parts = [body, barrel, handle]
    gun = trimesh.util.concatenate(gun_parts)

    return gun


def create_generic_weapon_mesh():
    """Create a generic weapon"""
    return trimesh.creation.capsule(radius=0.2, height=1.5)


def add_spike_detail(mesh):
    """Add spike details to mesh surface"""
    # Placeholder for adding spikes
    return mesh


def create_default_mesh():
    """Create a default interesting mesh when no specific shape is detected"""
    # Create a more complex default mesh using procedural generation
    return create_procedural_mesh("abstract geometric shape")

def preprocess_reference_image(image_path):
    """
    Preprocess reference image for future AI integration
    
    Args:
        image_path (str): Path to reference image
        
    Returns:
        Processed image data or None if not supported
    """
    # Placeholder for future image conditioning with AI models
    logging.info(f"Reference image provided: {image_path}")
    return None
