import os
import logging
import trimesh
import tempfile
import subprocess
import sys

# Import export engine (optional)
EXPORT_AVAILABLE = True
try:
    from instance.ai_modules.export_engine import create_export_engine, ExportFormat, OptimizationConfig
    export_engine = create_export_engine()
except Exception as e:
    logging.warning(f"Export engine not available, using simple fallbacks: {e}")
    EXPORT_AVAILABLE = False
    export_engine = None

def convert_to_fbx(obj_path, job_id):
    """
    Convert OBJ file to FBX format using Blender or fallback to OBJ
    
    Args:
        obj_path (str): Path to input OBJ file
        job_id (int): Job ID for output file naming
        
    Returns:
        str: Path to converted FBX file or original OBJ if conversion fails
    """
    try:
        logging.info(f"Converting {obj_path} to FBX format")
        
        # Try using Blender first (most reliable)
        try:
            return convert_with_blender(obj_path, job_id, 'fbx')
        except Exception as blender_error:
            logging.warning(f"Blender conversion failed: {blender_error}")
            
            # Fallback 1: try using trimesh if it has FBX support
            try:
                mesh = trimesh.load(obj_path)
                if mesh is None:
                    raise Exception("Failed to load OBJ file")
                
                output_filename = f"model_{job_id}.fbx"
                output_path = os.path.join("generated", output_filename)
                
                # Check if trimesh supports FBX export
                if hasattr(mesh, 'export') and 'fbx' in mesh.exporters_available():
                    mesh.export(output_path, file_type='fbx')
                    logging.info(f"FBX file saved to: {output_path}")
                    return output_path
                else:
                    raise Exception("FBX exporter not available in trimesh")
                    
            except Exception as trimesh_error:
                logging.warning(f"Trimesh FBX conversion failed: {trimesh_error}")
                
                # Fallback 2: try using export engine
                try:
                    if not EXPORT_AVAILABLE or export_engine is None:
                        raise Exception("Export engine unavailable")
                    mesh = trimesh.load(obj_path)
                    if mesh is None:
                        raise Exception("Failed to load OBJ file")
                    
                    output_filename = f"model_{job_id}.fbx"
                    output_path = os.path.join("generated", output_filename)
                    
                    success = export_engine.export_model(mesh, ExportFormat.FBX, output_path)
                    if success:
                        logging.info(f"FBX file saved to: {output_path}")
                        return output_path
                    else:
                        raise Exception("Export engine failed")
                        
                except Exception as export_engine_error:
                    logging.warning(f"Export engine FBX conversion failed: {export_engine_error}")
                    
                    # Final fallback: return the OBJ file path
                    logging.info(f"FBX conversion not available, using OBJ file: {obj_path}")
                    return obj_path
        
    except Exception as e:
        logging.error(f"Error converting to FBX: {str(e)}")
        # Return original OBJ file as fallback
        logging.info(f"Using original OBJ file as fallback: {obj_path}")
        return obj_path

def convert_to_blend(obj_path, job_id):
    """
    Convert OBJ file to Blender format using Blender Python API
    
    Args:
        obj_path (str): Path to input OBJ file
        job_id (int): Job ID for output file naming
        
    Returns:
        str: Path to converted Blend file or None if conversion fails
    """
    try:
        logging.info(f"Converting {obj_path} to Blend format")
        return convert_with_blender(obj_path, job_id, 'blend')
        
    except Exception as e:
        logging.warning(f"Blender conversion failed: {str(e)}")
        
        # Fallback: try using export engine
        try:
            if not EXPORT_AVAILABLE or export_engine is None:
                raise Exception("Export engine unavailable")
            mesh = trimesh.load(obj_path)
            if mesh is None:
                raise Exception("Failed to load OBJ file")
            
            output_filename = f"model_{job_id}.blend"
            output_path = os.path.join("generated", output_filename)
            
            success = export_engine.export_model(mesh, ExportFormat.RBXM, output_path)
            if success:
                logging.info(f"Blend file saved to: {output_path}")
                return output_path
            else:
                raise Exception("Export engine failed")
                
        except Exception as export_engine_error:
            logging.warning(f"Export engine Blend conversion failed: {export_engine_error}")
            # Return None instead of raising - this makes it optional
            return None

def convert_with_blender(obj_path, job_id, output_format):
    """
    Convert using Blender command line interface
    
    Args:
        obj_path (str): Path to input OBJ file
        job_id (int): Job ID for output file naming
        output_format (str): 'fbx' or 'blend'
        
    Returns:
        str: Path to converted file
    """
    try:
        # Check if Blender is available
        blender_cmd = find_blender_executable()
        
        if not blender_cmd:
            raise Exception("Blender not found in system PATH")
        
        # Output path
        if output_format == 'blend':
            output_filename = f"model_{job_id}.blend"
            output_path = os.path.join("generated", output_filename)
        else:
            output_filename = f"model_{job_id}.fbx"
            output_path = os.path.join("generated", output_filename)
        
        # Create Blender script
        script_content = create_blender_script(obj_path, output_path, output_format)
        
        # Write script to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as script_file:
            script_file.write(script_content)
            script_path = script_file.name
        
        try:
            # Run Blender with the script
            cmd = [
                blender_cmd,
                '--background',
                '--python', script_path
            ]
            
            logging.info(f"Running Blender command: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode != 0:
                raise Exception(f"Blender conversion failed: {result.stderr}")
            
            if not os.path.exists(output_path):
                raise Exception("Output file was not created")
            
            logging.info(f"{output_format.upper()} file saved to: {output_path}")
            return output_path
            
        finally:
            # Clean up temporary script file
            try:
                os.unlink(script_path)
            except:
                pass
                
    except subprocess.TimeoutExpired:
        raise Exception("Blender conversion timed out")
    except Exception as e:
        logging.error(f"Error in Blender conversion: {str(e)}")
        raise

def find_blender_executable():
    """
    Find Blender executable in common locations (Windows and Unix)
    
    Returns:
        str or None: Path to Blender executable
    """
    import platform
    
    # Common Blender executable names
    blender_names = ['blender', 'blender3d']
    
    # Try system PATH first
    for name in blender_names:
        try:
            if platform.system() == 'Windows':
                # On Windows, try 'where' command
                result = subprocess.run(['where', name], capture_output=True, text=True)
            else:
                # On Unix/Linux, try 'which' command
                result = subprocess.run(['which', name], capture_output=True, text=True)
            
            if result.returncode == 0:
                # Get the first path from the output
                paths = result.stdout.strip().split('\n')
                if paths and paths[0]:
                    return paths[0]
        except:
            pass
    
    # Try common installation paths based on OS
    if platform.system() == 'Windows':
        # Windows common paths
        common_paths = [
            r'C:\Program Files\Blender Foundation\Blender 4.4\blender.exe',
            r'C:\Program Files\Blender Foundation\Blender 4.3\blender.exe',
            r'C:\Program Files\Blender Foundation\Blender 4.2\blender.exe',
            r'C:\Program Files\Blender Foundation\Blender 4.1\blender.exe',
            r'C:\Program Files\Blender Foundation\Blender 4.0\blender.exe',
            r'C:\Program Files\Blender Foundation\Blender 3.6\blender.exe',
            r'C:\Program Files\Blender Foundation\Blender 3.5\blender.exe',
            r'C:\Program Files\Blender Foundation\Blender 3.4\blender.exe',
            r'C:\Program Files\Blender Foundation\Blender 3.3\blender.exe',
            r'C:\Program Files\Blender Foundation\Blender 3.2\blender.exe',
            r'C:\Program Files\Blender Foundation\Blender 3.1\blender.exe',
            r'C:\Program Files\Blender Foundation\Blender 3.0\blender.exe',
            r'C:\Program Files\Blender\blender.exe',
            r'C:\blender\blender.exe',
            # Check Program Files (x86) for 32-bit installations
            r'C:\Program Files (x86)\Blender Foundation\Blender 4.4\blender.exe',
            r'C:\Program Files (x86)\Blender Foundation\Blender 4.3\blender.exe',
            r'C:\Program Files (x86)\Blender Foundation\Blender 4.2\blender.exe',
            r'C:\Program Files (x86)\Blender Foundation\Blender 4.1\blender.exe',
            r'C:\Program Files (x86)\Blender Foundation\Blender 4.0\blender.exe',
            r'C:\Program Files (x86)\Blender Foundation\Blender 3.6\blender.exe',
            r'C:\Program Files (x86)\Blender Foundation\Blender 3.5\blender.exe',
            r'C:\Program Files (x86)\Blender Foundation\Blender 3.4\blender.exe',
            r'C:\Program Files (x86)\Blender Foundation\Blender 3.3\blender.exe',
            r'C:\Program Files (x86)\Blender Foundation\Blender 3.2\blender.exe',
            r'C:\Program Files (x86)\Blender Foundation\Blender 3.1\blender.exe',
            r'C:\Program Files (x86)\Blender Foundation\Blender 3.0\blender.exe',
            r'C:\Program Files (x86)\Blender\blender.exe',
        ]
    else:
        # Unix/Linux common paths
        common_paths = [
            '/usr/bin/blender',
            '/usr/local/bin/blender',
            '/opt/blender/blender',
            '/snap/bin/blender',
            '/Applications/Blender.app/Contents/MacOS/Blender',  # macOS
        ]
    
    for path in common_paths:
        if os.path.exists(path):
            logging.info(f"Found Blender at: {path}")
            return path
    
    logging.warning("Blender executable not found in common locations")
    return None

def create_blender_script(obj_path, output_path, output_format):
    """
    Create Blender Python script for conversion
    
    Args:
        obj_path (str): Path to input OBJ file
        output_path (str): Path for output file
        output_format (str): 'fbx' or 'blend'
        
    Returns:
        str: Blender Python script content
    """
    script = f'''
import bpy
import os
import sys

# Clear default scene
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

try:
    # Import OBJ file
    bpy.ops.import_scene.obj(filepath="{obj_path}")
    
    # Ensure output directory exists
    os.makedirs(os.path.dirname("{output_path}"), exist_ok=True)
    
    if "{output_format}" == "blend":
        # Save as Blend file
        bpy.ops.wm.save_as_mainfile(filepath="{output_path}")
    elif "{output_format}" == "fbx":
        # Export as FBX
        bpy.ops.export_scene.fbx(filepath="{output_path}")
    
    print(f"Successfully converted to {output_format.upper()}: {output_path}")
    
except Exception as e:
    print(f"Error during conversion: {{str(e)}}")
    sys.exit(1)
'''
    return script

def create_simple_mesh_fallback(job_id):
    """
    Create a simple fallback mesh when conversion fails
    
    Args:
        job_id (int): Job ID for file naming
        
    Returns:
        tuple: (fbx_path, blend_path)
    """
    try:
        logging.info("Creating fallback mesh")
        
        # Create a simple cube mesh
        mesh = trimesh.creation.box(extents=[2.0, 2.0, 2.0])
        
        # Export as OBJ first
        obj_filename = f"fallback_{job_id}.obj"
        obj_path = os.path.join("generated", obj_filename)
        mesh.export(obj_path)
        
        # Try to convert to FBX and Blend
        fbx_path = None
        blend_path = None
        
        try:
            fbx_path = convert_to_fbx(obj_path, f"fallback_{job_id}")
        except:
            logging.warning("Failed to create fallback FBX")
        
        try:
            blend_path = convert_to_blend(obj_path, f"fallback_{job_id}")
        except:
            logging.warning("Failed to create fallback Blend")
        
        # If both conversions failed, try using export engine directly
        if fbx_path is None and blend_path is None and EXPORT_AVAILABLE and export_engine is not None:
            try:
                # Export FBX using export engine
                fbx_filename = f"fallback_{job_id}.fbx"
                fbx_path = os.path.join("generated", fbx_filename)
                success = export_engine.export_model(mesh, ExportFormat.FBX, fbx_path)
                if not success:
                    fbx_path = None
                    
                # Export Blend using export engine
                blend_filename = f"fallback_{job_id}.blend"
                blend_path = os.path.join("generated", blend_filename)
                success = export_engine.export_model(mesh, ExportFormat.RBXM, blend_path)
                if not success:
                    blend_path = None
            except Exception as export_engine_error:
                logging.warning(f"Export engine fallback failed: {export_engine_error}")
        
        return fbx_path, blend_path
        
    except Exception as e:
        logging.error(f"Failed to create fallback mesh: {str(e)}")
        return None, None
