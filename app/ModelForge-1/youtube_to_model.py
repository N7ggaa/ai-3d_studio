import os
import cv2
import yt_dlp
import logging
import tempfile
import shutil
import trimesh
import numpy as np
from typing import List, Optional, Dict, Any
from pathlib import Path
import re
import json


class YouTubeTo3D:
    """
    A class to handle YouTube video to 3D model conversion
    Downloads video, extracts frames, and generates 3D models based on content
    """

    def __init__(self, output_dir: str = "generated/youtube_models"):
        """
        Initialize the YouTube to 3D converter

        Args:
            output_dir (str): Directory to save extracted frames and models
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Create subdirectories
        self.frames_dir = self.output_dir / "frames"
        self.models_dir = self.output_dir / "models"
        self.frames_dir.mkdir(exist_ok=True)
        self.models_dir.mkdir(exist_ok=True)

        # Configure logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def download_video(self, youtube_url: str, quality: str = "best[height<=720]") -> Optional[str]:
        """
        Download YouTube video to temporary file with comprehensive error handling

        Args:
            youtube_url (str): YouTube video URL
            quality (str): Video quality preference

        Returns:
            str: Path to downloaded video file, None if failed
        """
        # Input validation
        if not youtube_url or not isinstance(youtube_url, str):
            self.logger.error("Invalid YouTube URL provided")
            return None

        # Basic URL validation
        if not ('youtube.com' in youtube_url or 'youtu.be' in youtube_url):
            self.logger.error(f"Invalid YouTube URL format: {youtube_url}")
            return None

        try:
            self.logger.info(f"Downloading video from: {youtube_url}")

            # Create temporary directory for download
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)

                # yt-dlp options
                ydl_opts = {
                    'format': quality,
                    'outtmpl': str(temp_path / 'video.%(ext)s'),
                    'quiet': False,
                    'no_warnings': False,
                }

                # Download video
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(youtube_url, download=True)
                    video_file = temp_path / f"video.{info['ext']}"

                    if video_file.exists():
                        # Copy to our output directory with unique name
                        video_id = info.get('id', 'unknown')
                        output_file = self.output_dir / f"{video_id}_video.{info['ext']}"

                        shutil.copy2(video_file, output_file)
                        self.logger.info(f"Video downloaded successfully: {output_file}")
                        return str(output_file)
                    else:
                        self.logger.error("Video file not found after download")
                        return None

        except Exception as e:
            self.logger.error(f"Error downloading video: {str(e)}")
            return None

    def extract_frames(self, video_path: str, frame_interval: int = 30,
                      max_frames: int = 50) -> List[str]:
        """
        Extract frames from video at specified intervals with comprehensive error handling

        Args:
            video_path (str): Path to video file
            frame_interval (int): Extract every Nth frame
            max_frames (int): Maximum number of frames to extract

        Returns:
            List[str]: List of paths to extracted frame images
        """
        # Input validation
        if not video_path or not os.path.exists(video_path):
            self.logger.error(f"Video file not found: {video_path}")
            return []

        if frame_interval < 1:
            frame_interval = 1
            self.logger.warning("Frame interval too low, using 1")

        if max_frames < 1:
            max_frames = 1
            self.logger.warning("Max frames too low, using 1")

        try:
            self.logger.info(f"Extracting frames from: {video_path}")

            if not os.path.exists(video_path):
                self.logger.error(f"Video file not found: {video_path}")
                return []

            # Open video file
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                self.logger.error(f"Could not open video file: {video_path}")
                return []

            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

            self.logger.info(f"Video FPS: {fps}, Total frames: {total_frames}")

            frame_paths = []
            frame_count = 0
            extracted_count = 0

            while frame_count < total_frames and extracted_count < max_frames:
                ret, frame = cap.read()
                if not ret:
                    break

                # Extract every frame_interval frames
                if frame_count % frame_interval == 0:
                    # Generate unique filename
                    frame_filename = f"frame_{extracted_count:04d}.jpg"
                    frame_path = self.frames_dir / frame_filename

                    # Save frame
                    cv2.imwrite(str(frame_path), frame)
                    frame_paths.append(str(frame_path))

                    extracted_count += 1
                    self.logger.info(f"Extracted frame {extracted_count}/{max_frames}")

                frame_count += 1

            cap.release()
            self.logger.info(f"Frame extraction completed. Extracted {len(frame_paths)} frames")
            return frame_paths

        except Exception as e:
            self.logger.error(f"Error extracting frames: {str(e)}")
            return []

    def analyze_frames(self, frame_paths: List[str]) -> Dict[str, Any]:
        """
        Analyze extracted frames to understand video content

        Args:
            frame_paths (List[str]): List of frame image paths

        Returns:
            Dict[str, Any]: Analysis results including dominant colors, objects, etc.
        """
        try:
            self.logger.info("Analyzing frames for content understanding")

            if not frame_paths:
                return {'error': 'No frames provided'}

            analysis = {
                'total_frames': len(frame_paths),
                'dominant_colors': [],
                'brightness_levels': [],
                'detected_shapes': [],
                'motion_level': 'unknown'
            }

            colors = []
            brightness_values = []

            for frame_path in frame_paths[:min(10, len(frame_paths))]:  # Analyze first 10 frames
                frame = cv2.imread(frame_path)
                if frame is None:
                    continue

                # Calculate average color
                avg_color = np.mean(frame, axis=(0, 1))
                colors.append(avg_color.tolist())

                # Calculate brightness
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                brightness = np.mean(gray)
                brightness_values.append(brightness)

                # Simple shape detection (edges)
                edges = cv2.Canny(gray, 50, 150)
                edge_density = np.sum(edges > 0) / (edges.shape[0] * edges.shape[1])

                if edge_density > 0.1:
                    analysis['detected_shapes'].append('complex')
                else:
                    analysis['detected_shapes'].append('simple')

            if colors:
                analysis['dominant_colors'] = np.mean(colors, axis=0).tolist()
                analysis['brightness_levels'] = brightness_values

                # Determine overall brightness
                avg_brightness = np.mean(brightness_values)
                if avg_brightness < 80:
                    analysis['overall_tone'] = 'dark'
                elif avg_brightness > 170:
                    analysis['overall_tone'] = 'bright'
                else:
                    analysis['overall_tone'] = 'medium'

            # Estimate motion level (compare first and last frame)
            if len(frame_paths) >= 2:
                first_frame = cv2.imread(frame_paths[0])
                last_frame = cv2.imread(frame_paths[-1])

                if first_frame is not None and last_frame is not None:
                    diff = cv2.absdiff(first_frame, last_frame)
                    motion_score = np.mean(diff)

                    if motion_score > 50:
                        analysis['motion_level'] = 'high'
                    elif motion_score > 20:
                        analysis['motion_level'] = 'medium'
                    else:
                        analysis['motion_level'] = 'low'

            self.logger.info(f"Frame analysis completed: {analysis}")
            return analysis

        except Exception as e:
            self.logger.error(f"Error analyzing frames: {str(e)}")
            return {'error': str(e)}

    def generate_3d_model(self, prompt: str, frame_paths: List[str],
                         output_format: str = "obj") -> Optional[str]:
        """
        Generate 3D model based on video content and prompt

        Args:
            prompt (str): Text prompt for model generation
            frame_paths (List[str]): List of frame image paths
            output_format (str): Output format ("obj", "fbx", "gltf")

        Returns:
            str: Path to generated 3D model file, None if failed
        """
        try:
            self.logger.info(f"Generating 3D model for prompt: {prompt}")

            if not frame_paths:
                self.logger.error("No frames provided for 3D generation")
                return None

            # Analyze video content
            analysis = self.analyze_frames(frame_paths)

            # Generate 3D model based on prompt and analysis
            mesh = self._create_mesh_from_analysis(prompt, analysis)

            if mesh is None:
                self.logger.error("Failed to create 3D mesh")
                return None

            # Generate unique filename
            import time
            timestamp = int(time.time())
            model_filename = f"youtube_model_{timestamp}.{output_format}"
            model_path = self.models_dir / model_filename

            # Export mesh
            if output_format.lower() == "obj":
                mesh.export(str(model_path))
            elif output_format.lower() == "fbx":
                # For FBX, we'd need additional libraries or Blender
                # For now, export as OBJ and note FBX conversion needed
                obj_path = model_path.with_suffix('.obj')
                mesh.export(str(obj_path))
                self.logger.warning("FBX export not implemented, saved as OBJ")
                return str(obj_path)
            elif output_format.lower() == "gltf":
                # For GLTF, we'd need additional libraries
                obj_path = model_path.with_suffix('.obj')
                mesh.export(str(obj_path))
                self.logger.warning("GLTF export not implemented, saved as OBJ")
                return str(obj_path)
            else:
                mesh.export(str(model_path))

            # Save analysis data
            analysis_file = model_path.with_suffix('.json')
            with open(analysis_file, 'w') as f:
                json.dump({
                    'prompt': prompt,
                    'analysis': analysis,
                    'frame_count': len(frame_paths),
                    'output_format': output_format
                }, f, indent=2)

            self.logger.info(f"3D model generated successfully: {model_path}")
            return str(model_path)

        except Exception as e:
            self.logger.error(f"Error generating 3D model: {str(e)}")
            return None

    def _create_mesh_from_analysis(self, prompt: str, analysis: Dict[str, Any]) -> Optional[trimesh.Trimesh]:
        """
        Create 3D mesh based on prompt and video analysis

        Args:
            prompt (str): Text prompt
            analysis (Dict[str, Any]): Video analysis results

        Returns:
            trimesh.Trimesh: Generated mesh or None if failed
        """
        try:
            prompt_lower = prompt.lower()

            # Determine mesh type based on prompt and analysis
            if any(word in prompt_lower for word in ['building', 'house', 'structure']):
                return self._create_building_mesh(analysis)
            elif any(word in prompt_lower for word in ['character', 'person', 'human']):
                return self._create_character_mesh(analysis)
            elif any(word in prompt_lower for word in ['vehicle', 'car', 'spaceship']):
                return self._create_vehicle_mesh(analysis)
            elif any(word in prompt_lower for word in ['landscape', 'terrain', 'environment']):
                return self._create_terrain_mesh(analysis)
            else:
                # Default: create based on dominant colors and shapes
                return self._create_default_mesh(analysis)

        except Exception as e:
            self.logger.error(f"Error creating mesh from analysis: {str(e)}")
            return None

    def _create_building_mesh(self, analysis: Dict[str, Any]) -> trimesh.Trimesh:
        """Create a building-like mesh"""
        # Main structure
        main_body = trimesh.creation.box(extents=[2.0, 2.0, 3.0])

        # Roof
        roof = trimesh.creation.cone(radius=1.2, height=1.0)
        roof.apply_translation([0, 0, 2.0])

        # Combine
        building = trimesh.util.concatenate([main_body, roof])
        return building

    def _create_character_mesh(self, analysis: Dict[str, Any]) -> trimesh.Trimesh:
        """Create a character-like mesh"""
        # Body (cylinder)
        body = trimesh.creation.cylinder(radius=0.5, height=1.5)

        # Head (sphere)
        head = trimesh.creation.uv_sphere(radius=0.3)
        head.apply_translation([0, 0, 1.2])

        # Arms (cylinders)
        left_arm = trimesh.creation.cylinder(radius=0.1, height=1.0)
        left_arm.apply_translation([-0.7, 0, 0.5])

        right_arm = trimesh.creation.cylinder(radius=0.1, height=1.0)
        right_arm.apply_translation([0.7, 0, 0.5])

        # Combine
        character = trimesh.util.concatenate([body, head, left_arm, right_arm])
        return character

    def _create_vehicle_mesh(self, analysis: Dict[str, Any]) -> trimesh.Trimesh:
        """Create a vehicle-like mesh"""
        # Main body
        body = trimesh.creation.box(extents=[3.0, 1.5, 1.0])

        # Wheels
        wheels = []
        wheel_positions = [
            [1.0, 0.8, -0.5],
            [1.0, -0.8, -0.5],
            [-1.0, 0.8, -0.5],
            [-1.0, -0.8, -0.5]
        ]

        for pos in wheel_positions:
            wheel = trimesh.creation.cylinder(radius=0.3, height=0.2)
            wheel.apply_translation(pos)
            wheels.append(wheel)

        # Combine
        vehicle_parts = [body] + wheels
        vehicle = trimesh.util.concatenate(vehicle_parts)
        return vehicle

    def _create_terrain_mesh(self, analysis: Dict[str, Any]) -> trimesh.Trimesh:
        """Create a terrain-like mesh"""
        # Create a simple terrain using noise-like approach
        size = 20
        vertices = []
        faces = []

        # Generate vertices in a grid
        for i in range(size):
            for j in range(size):
                x = (i - size/2) * 0.5
                y = (j - size/2) * 0.5
                # Simple height variation
                z = np.sin(i * 0.3) * np.cos(j * 0.3) * 2.0
                vertices.append([x, y, z])

        # Generate faces
        for i in range(size - 1):
            for j in range(size - 1):
                # Two triangles per quad
                v1 = i * size + j
                v2 = i * size + j + 1
                v3 = (i + 1) * size + j
                v4 = (i + 1) * size + j + 1

                faces.append([v1, v2, v3])
                faces.append([v2, v3, v4])

        # Create mesh
        terrain = trimesh.Trimesh(vertices=vertices, faces=faces)
        return terrain

    def _create_default_mesh(self, analysis: Dict[str, Any]) -> trimesh.Trimesh:
        """Create a default interesting mesh"""
        # Create a torus as default
        torus = trimesh.creation.torus(major_radius=1.5, minor_radius=0.5)

        # Add some variation based on analysis
        if 'dominant_colors' in analysis:
            colors = analysis['dominant_colors']
            if len(colors) >= 3:
                # Scale based on brightness
                brightness = sum(colors[:3]) / 3.0 / 255.0
                scale_factor = 0.5 + brightness * 0.5
                torus.apply_scale(scale_factor)

        return torus

    def process_youtube_url(self, youtube_url: str, prompt: str = "",
                          frame_interval: int = 30) -> Optional[str]:
        """
        Complete pipeline: download video, extract frames, generate 3D model

        Args:
            youtube_url (str): YouTube video URL
            prompt (str): Text prompt for model generation
            frame_interval (int): Frame extraction interval

        Returns:
            str: Path to generated 3D model file, None if failed
        """
        try:
            self.logger.info(f"Starting complete YouTube to 3D pipeline for: {youtube_url}")

            # Step 1: Download video
            video_path = self.download_video(youtube_url)
            if not video_path:
                return None

            # Step 2: Extract frames
            frame_paths = self.extract_frames(video_path, frame_interval)
            if not frame_paths:
                return None

            # Step 3: Generate 3D model
            if not prompt:
                prompt = "A 3D model based on the video content"

            model_path = self.generate_3d_model(prompt, frame_paths)

            # Clean up video file
            try:
                os.unlink(video_path)
                self.logger.info("Cleaned up temporary video file")
            except Exception as e:
                self.logger.warning(f"Could not clean up video file: {e}")

            return model_path

        except Exception as e:
            self.logger.error(f"Error in complete pipeline: {str(e)}")
            return None

    def get_video_info(self, youtube_url: str) -> Dict[str, Any]:
        """
        Get video information without downloading

        Args:
            youtube_url (str): YouTube video URL

        Returns:
            Dict[str, Any]: Video information
        """
        try:
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info = ydl.extract_info(youtube_url, download=False)
                return {
                    'title': info.get('title', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'uploader': info.get('uploader', 'Unknown'),
                    'view_count': info.get('view_count', 0),
                    'thumbnail': info.get('thumbnail', ''),
                    'description': info.get('description', '')[:500] + '...' if info.get('description') else ''
                }
        except Exception as e:
            self.logger.error(f"Error getting video info: {str(e)}")
            return {'error': str(e)}


# Standalone functions for backward compatibility
def download_youtube_video(url: str) -> Optional[str]:
    """Download YouTube video and return path"""
    processor = YouTubeTo3D()
    return processor.download_video(url)


def extract_video_frames(video_path: str) -> List[str]:
    """Extract frames from video and return frame paths"""
    processor = YouTubeTo3D()
    return processor.extract_frames(video_path)


def generate_3d_from_video(prompt: str, frame_paths: List[str]) -> Optional[str]:
    """Generate 3D model from video frames"""
    processor = YouTubeTo3D()
    return processor.generate_3d_model(prompt, frame_paths)