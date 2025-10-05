"""
Video Processor for AI 3D Model Generator
Handles video frame extraction and processing for 3D model generation.
"""

import os
import cv2
import numpy as np
from typing import List, Tuple, Optional, Dict, Any, Union
import json
from dataclasses import dataclass, asdict, field
import subprocess
import shutil
from pathlib import Path
import time
from enum import Enum, auto

class ProcessingMode(Enum):
    EXTRACT = auto()
    PROCESS = auto()
    DETECT = auto()
    ALL = auto()

@dataclass
class DetectionResult:
    """Class to store object detection results."""
    class_name: str
    confidence: float
    bbox: Tuple[int, int, int, int]  # x, y, width, height
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'class': self.class_name,
            'confidence': float(self.confidence),
            'bbox': self.bbox
        }

@dataclass
class FrameMetadata:
    """Class to store metadata for processed frames."""
    frame_number: int
    timestamp: float
    has_foreground: bool = False
    objects: List[Dict[str, Any]] = field(default_factory=list)
    processing_time: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'frame_number': self.frame_number,
            'timestamp': self.timestamp,
            'has_foreground': self.has_foreground,
            'objects': [obj.to_dict() if hasattr(obj, 'to_dict') else obj for obj in self.objects],
            'processing_time': self.processing_time
        }

@dataclass
class VideoInfo:
    """Class to store video metadata."""
    width: int
    height: int
    fps: float
    frame_count: int
    duration: float
    codec: str
    format: str
    bitrate: int
    has_audio: bool
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_video(cls, video_path: str) -> 'VideoInfo':
        """Extract video information using OpenCV."""
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
            
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise IOError(f"Could not open video: {video_path}")
            
        try:
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = frame_count / fps if fps > 0 else 0
            
            # Get codec information
            codec = int(cap.get(cv2.CAP_PROP_FOURCC))
            codec_name = "".join([chr((codec >> 8 * i) & 0xFF) for i in range(4)])
            
            # Get bitrate (may not be available in all formats)
            bitrate = int(cap.get(cv2.CAP_PROP_BITRATE)) if cap.get(cv2.CAP_PROP_BITRATE) > 0 else 0
            
            # Check if audio exists (this is a best-effort approach)
            # We'll assume audio exists if the video file has a common audio extension
            has_audio = False
            try:
                # Check common audio extensions in the filename
                audio_extensions = ['.mp3', '.wav', '.aac', '.ogg', '.wma']
                base, ext = os.path.splitext(video_path.lower())
                has_audio = ext in audio_extensions
            except:
                pass
                
            return cls(
                width=width,
                height=height,
                fps=fps,
                frame_count=frame_count,
                duration=duration,
                codec=codec_name,
                format=os.path.splitext(video_path)[1].lstrip('.').lower(),
                bitrate=bitrate,
                has_audio=has_audio
            )
            
        finally:
            cap.release()

class BackgroundRemover:
    """Handles background removal from video frames."""
    
    def __init__(self, method: str = 'MOG2', history: int = 500, var_threshold: int = 16, 
                 detect_shadows: bool = True, learning_rate: float = 0.001):
        """Initialize the background remover.
        
        Args:
            method: Background subtraction method ('MOG2' or 'KNN')
            history: Length of the history for background model
            var_threshold: Threshold for the squared Mahalanobis distance
            detect_shadows: Whether to detect shadows
            learning_rate: Learning rate for the background model
        """
        self.method = method.upper()
        self.history = history
        self.var_threshold = var_threshold
        self.detect_shadows = detect_shadows
        self.learning_rate = learning_rate
        self.background_subtractor = None
        
    def initialize(self, frame: np.ndarray):
        """Initialize the background subtractor with the first frame."""
        if self.method == 'MOG2':
            self.background_subtractor = cv2.createBackgroundSubtractorMOG2(
                history=self.history,
                varThreshold=self.var_threshold,
                detectShadows=self.detect_shadows
            )
        else:  # KNN
            self.background_subtractor = cv2.createBackgroundSubtractorKNN(
                history=self.history,
                dist2Threshold=self.var_threshold,
                detectShadows=self.detect_shadows
            )
        
        # Initialize with first frame
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        self.background_subtractor.apply(gray, learningRate=1.0)
    
    def remove_background(self, frame: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """Remove background from a frame.
        
        Args:
            frame: Input frame (BGR format)
            
        Returns:
            Tuple of (mask, foreground) where mask is the binary mask and
            foreground is the original frame with background removed
        """
        if self.background_subtractor is None:
            self.initialize(frame)
        
        # Convert to grayscale for background subtraction
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Apply background subtraction
        fg_mask = self.background_subtractor.apply(gray, learningRate=self.learning_rate)
        
        # Remove shadow (value 127 in the mask)
        if self.detect_shadows:
            fg_mask[fg_mask == 127] = 0
        
        # Apply morphological operations to clean up the mask
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_OPEN, kernel)
        fg_mask = cv2.morphologyEx(fg_mask, cv2.MORPH_CLOSE, kernel)
        
        # Apply mask to original frame
        foreground = cv2.bitwise_and(frame, frame, mask=fg_mask)
        
        return fg_mask, foreground

class ObjectDetector:
    """Handles object detection in video frames."""
    
    def __init__(self, model_path: Optional[str] = None, confidence_threshold: float = 0.5):
        """Initialize the object detector.
        
        Args:
            model_path: Path to the object detection model
            confidence_threshold: Minimum confidence score for detections
        """
        self.confidence_threshold = confidence_threshold
        self.net = None
        self.classes = []
        
        if model_path and os.path.exists(model_path):
            self._load_model(model_path)
    
    def _load_model(self, model_path: str):
        """Load the object detection model."""
        # This is a placeholder - in a real implementation, this would load
        # a pre-trained model like YOLO, SSD, or Faster R-CNN
        pass
    
    def detect(self, frame: np.ndarray) -> List[DetectionResult]:
        """Detect objects in a frame.
        
        Args:
            frame: Input frame (BGR format)
            
        Returns:
            List of DetectionResult objects
        """
        # This is a placeholder - in a real implementation, this would run
        # the object detection model on the frame
        return []

class VideoProcessor:
    """Handles video processing tasks for the AI 3D Model Generator."""
    
    def __init__(self, output_dir: str = "output", temp_dir: str = "temp"):
        """Initialize the VideoProcessor.
        
        Args:
            output_dir: Directory to save processed outputs
            temp_dir: Directory for temporary files
        """
        self.output_dir = os.path.abspath(output_dir)
        self.temp_dir = os.path.abspath(temp_dir)
        
        # Create directories if they don't exist
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)
        
        # Initialize background remover and object detector
        self.background_remover = None
        self.object_detector = None
        self._initialized = False
    
    def get_video_info(self, video_path: str) -> VideoInfo:
        """Get information about a video file.
        
        Args:
            video_path: Path to the video file
            
        Returns:
            VideoInfo object containing video metadata
        """
        return VideoInfo.from_video(video_path)
    
    def initialize_processing(
        self,
        remove_background: bool = False,
        detect_objects: bool = False,
        **kwargs
    ):
        """Initialize processing modules.
        
        Args:
            remove_background: Whether to enable background removal
            detect_objects: Whether to enable object detection
            **kwargs: Additional arguments for the modules
        """
        if remove_background:
            self.background_remover = BackgroundRemover(
                method=kwargs.get('bg_method', 'MOG2'),
                history=kwargs.get('bg_history', 500),
                var_threshold=kwargs.get('bg_var_threshold', 16),
                detect_shadows=kwargs.get('bg_detect_shadows', True),
                learning_rate=kwargs.get('bg_learning_rate', 0.001)
            )
        
        if detect_objects:
            self.object_detector = ObjectDetector(
                model_path=kwargs.get('model_path'),
                confidence_threshold=kwargs.get('confidence_threshold', 0.5)
            )
        
        self._initialized = True
    
    def process_frame(
        self,
        frame: np.ndarray,
        frame_number: int,
        timestamp: float,
        remove_background: bool = False,
        detect_objects: bool = False
    ) -> Tuple[np.ndarray, FrameMetadata]:
        """Process a single video frame.
        
        Args:
            frame: Input frame (BGR format)
            frame_number: Frame number
            timestamp: Timestamp in seconds
            remove_background: Whether to remove background
            detect_objects: Whether to detect objects
            
        Returns:
            Tuple of (processed_frame, metadata)
        """
        start_time = time.time()
        metadata = FrameMetadata(frame_number=frame_number, timestamp=timestamp)
        processed_frame = frame.copy()
        
        # Apply background removal
        if remove_background and self.background_remover:
            try:
                fg_mask, processed_frame = self.background_remover.remove_background(frame)
                metadata.has_foreground = cv2.countNonZero(fg_mask) > 0
            except Exception as e:
                print(f"Error in background removal: {e}")
        
        # Run object detection
        if detect_objects and self.object_detector:
            try:
                detections = self.object_detector.detect(processed_frame)
                metadata.objects = [det for det in detections 
                                 if det.confidence >= self.object_detector.confidence_threshold]
            except Exception as e:
                print(f"Error in object detection: {e}")
        
        metadata.processing_time = time.time() - start_time
        return processed_frame, metadata
    
    def extract_audio(
        self,
        video_path: str,
        output_path: Optional[str] = None,
        format: str = 'mp3',
        overwrite: bool = False
    ) -> Optional[str]:
        """Extract audio from a video file using FFmpeg if available, with OpenCV fallback.
        
        Args:
            video_path: Path to the input video file.
            output_path: Path to save the extracted audio. If None, generates a path in the same
                       directory as the video with '_audio' suffix.
            format: Output audio format ('mp3', 'wav', 'aac', etc.). Defaults to 'mp3'.
            overwrite: If True, overwrite existing output file. Defaults to False.
            
        Returns:
            str: Path to the extracted audio file if successful, None otherwise.
            
        Raises:
            FileNotFoundError: If the input video file doesn't exist.
            RuntimeError: If there's an error during audio extraction.
        """
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")
            
        # Validate output format
        format = format.lower()
        if format not in ['mp3', 'wav', 'aac', 'ogg', 'flac']:
            format = 'mp3'  # Default to mp3 if unsupported format provided
            
        # Check if video has audio
        try:
            video_info = self.get_video_info(video_path)
            if not video_info.has_audio:
                print(f"No audio stream found in {video_path}")
                return None
        except Exception as e:
            print(f"Error checking audio stream: {e}")
            return None
        
        # Generate output path if not provided
        if output_path is None:
            base_name = os.path.splitext(os.path.basename(video_path))[0]
            output_path = os.path.join(
                os.path.dirname(video_path),
                f"{base_name}_audio.{format}"
            )
        else:
            # Ensure output directory exists
            os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        
        # Check if output file exists and should not be overwritten
        if os.path.exists(output_path) and not overwrite:
            print(f"Audio file already exists, skipping: {output_path}")
            return output_path
            
        print(f"Extracting audio to: {output_path}")
        
        # Try using FFmpeg first (better audio support)
        try:
            import subprocess
            
            # Use ffmpeg if available
            try:
                # Create command based on format
                if format == 'mp3':
                    cmd = [
                        'ffmpeg', '-y',
                        '-i', video_path,
                        '-q:a', '0',        # Best quality variable bitrate
                        '-map', 'a',        # Extract only audio
                        '-f', 'mp3',        # Force MP3 format
                        output_path
                    ]
                else:
                    cmd = [
                        'ffmpeg', '-y',
                        '-i', video_path,
                        '-acodec', 'copy' if format == 'aac' else 'pcm_s16le',
                        '-f', format,
                        output_path
                    ]
                
                # Run FFmpeg command
                result = subprocess.run(
                    cmd,
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                    print(f"Successfully extracted audio to: {output_path}")
                    return output_path
                else:
                    print("FFmpeg completed but no output file was created")
                    # Fall through to OpenCV method
                    
            except (subprocess.CalledProcessError, FileNotFoundError) as e:
                print(f"FFmpeg not available or error occurred: {e}")
                # Fall through to OpenCV method
                
        except Exception as e:
            print(f"Error setting up FFmpeg: {e}")
            # Fall through to OpenCV method
        
        # Fallback to OpenCV (limited support)
        print("Falling back to OpenCV for audio extraction (limited support)")
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                print("Error: Could not open video file with OpenCV")
                return None
                
            # Get audio properties
            sample_rate = int(cap.get(cv2.CAP_PROP_AUDIO_SAMPLES_PER_SECOND))
            channels = int(cap.get(cv2.CAP_PROP_AUDIO_TOTAL_CHANNELS))
            
            if sample_rate == 0 or channels == 0:
                print("No audio stream detected in video")
                cap.release()
                return None
                
            print(f"Extracting audio with OpenCV - Sample rate: {sample_rate}Hz, Channels: {channels}")
            
            # Read audio frames
            audio_frames = []
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                audio_frames.append(frame)
                
            cap.release()
            
            if not audio_frames:
                print("No audio frames were read")
                return None
                
            # Save audio as WAV (OpenCV has limited audio format support)
            import wave
            import numpy as np
            
            # Convert frames to numpy array
            try:
                audio_data = np.concatenate(audio_frames, axis=0)
                
                # Ensure output is WAV format
                output_path = os.path.splitext(output_path)[0] + '.wav'
                
                with wave.open(output_path, 'wb') as wf:
                    wf.setnchannels(channels)
                    wf.setsampwidth(2)  # 16-bit
                    wf.setframerate(sample_rate)
                    wf.writeframes(audio_data.tobytes())
                
                print(f"Successfully extracted audio using OpenCV: {output_path}")
                return output_path
                
            except Exception as e:
                print(f"Error processing audio frames: {e}")
                return None
                
        except Exception as e:
            print(f"Error during OpenCV audio extraction: {e}")
            return None
            
    def process_video_for_3d(
        self,
        video_path: str,
        output_dir: Optional[str] = None,
        max_duration: Optional[float] = 30.0,  # Default to 30 seconds
        target_fps: Optional[float] = None,
        target_size: Optional[Tuple[int, int]] = (512, 512),
        remove_background: bool = True,
        detect_objects: bool = True,
        progress_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """Process a video for 3D model generation.
        
        This is a high-level method that handles the complete pipeline:
        1. Extract frames from the video
        2. Optionally remove background from frames
        3. Optionally detect objects in frames
        4. Prepare output for 3D model generation
        
        Args:
            video_path: Path to the input video file.
            output_dir: Directory to save processed frames. If None, creates a temp directory.
            max_duration: Maximum duration in seconds to process from the video.
            target_fps: Target frames per second. If None, uses the original video FPS.
            target_size: Target size as (width, height) for resizing frames.
            remove_background: Whether to remove background from frames.
            detect_objects: Whether to detect objects in frames.
            progress_callback: Optional callback function for progress updates.
            
        Returns:
            Dictionary containing paths to processed frames and metadata.
            
        Raises:
            FileNotFoundError: If the input video file is not found.
            RuntimeError: If there's an error during processing.
        """
        try:
            if not os.path.exists(video_path):
                raise FileNotFoundError(f"Video file not found: {video_path}")
            
            # Get video info
            video_info = self.get_video_info(video_path)
            
            # Calculate frame interval if target_fps is specified
            frame_interval = 1
            if target_fps is not None and target_fps < video_info.fps:
                frame_interval = int(round(video_info.fps / target_fps))
            
            # Calculate number of frames to extract based on max_duration
            max_frames = None
            if max_duration is not None:
                max_frames = int(min(max_duration * video_info.fps, video_info.frame_count))
            
            # Create output directory
            if output_dir is None:
                output_dir = tempfile.mkdtemp(prefix='video_3d_')
            else:
                os.makedirs(output_dir, exist_ok=True)
            
            # Initialize processing
            self.initialize_processing(
                remove_background=remove_background,
                detect_objects=detect_objects
            )
            
            # Extract frames with processing
            result = self.extract_frames(
                video_path=video_path,
                output_dir=output_dir,
                max_frames=max_frames,
                target_size=target_size,
                remove_background=remove_background,
                detect_objects=detect_objects,
                progress_callback=progress_callback
            )
            
            # Add additional metadata
            result.update({
                'video_info': {
                    'path': video_path,
                    'original_fps': video_info.fps,
                    'original_duration': video_info.duration,
                    'original_frame_count': video_info.frame_count,
                    'original_resolution': (video_info.width, video_info.height)
                },
                'processing_params': {
                    'target_fps': target_fps if target_fps is not None else video_info.fps,
                    'target_resolution': target_size,
                    'remove_background': remove_background,
                    'detect_objects': detect_objects,
                    'max_duration': max_duration
                }
            })
            
            # Save updated metadata
            metadata_path = os.path.join(output_dir, 'metadata.json')
            with open(metadata_path, 'w') as f:
                json.dump(result, f, indent=2, default=str)
            
            result['metadata_path'] = metadata_path
            return result
                
        except Exception as e:
            error_msg = f"Error processing video for 3D: {str(e)}"
            if progress_callback:
                progress_callback(1.0, error_msg)
            raise RuntimeError(error_msg) from e

    def extract_audio(
        self,
        video_path: str,
        output_path: Optional[str] = None,
        format: str = 'mp3',
        overwrite: bool = False
    ) -> Optional[str]:
        """Extract audio from a video file.
        
        Args:
            video_path: Path to the video file
            output_path: Output audio file path (default: output_dir/audio.ext)
            format: Output audio format (mp3, wav, etc.)
            overwrite: Whether to overwrite existing file
            
        Returns:
            Path to the extracted audio file, or None if no audio stream
        """
        try:
            # Check if video has audio
            if not self.get_video_info(video_path).has_audio:
                return None
                
            if output_path is None:
                video_name = os.path.splitext(os.path.basename(video_path))[0]
                output_path = os.path.join(self.output_dir, "audio", f"{video_name}.{format}")
        
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Skip if file exists and not overwriting
            if not overwrite and os.path.exists(output_path):
                return output_path
            
            # Extract audio using ffmpeg
            cmd = [
                'ffmpeg',
                '-y' if overwrite else '-n',
                '-i', video_path,
                '-vn',  # Disable video
                '-acodec', 'libmp3lame' if format == 'mp3' else 'pcm_s16le',
                '-ar', '44100',
                '-ac', '2',
                '-q:a', '2',  # Quality (0-9, 0=best)
                output_path
            ]
            
            subprocess.run(cmd, check=True, capture_output=True)
            return output_path
            
        except subprocess.CalledProcessError as e:
            print(f"Error extracting audio: {e.stderr.decode('utf-8', errors='ignore')}")
            return None
        except Exception as e:
            print(f"Unexpected error in extract_audio: {str(e)}")
            return None

def main():
    """Command-line interface for video processing."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Process video for 3D model generation.')
    
    # Required arguments
    parser.add_argument('video_path', type=str, help='Path to the input video file')
    
    # Output options
    parser.add_argument('--output', '-o', type=str, default='output', help='Output directory')
    parser.add_argument('--temp-dir', '-t', type=str, default='temp', help='Temporary directory')
    
    # Frame extraction options
    parser.add_argument('--start-time', type=float, default=0, help='Start time in seconds')
    parser.add_argument('--duration', type=float, help='Duration to process in seconds')
    parser.add_argument('--max-duration', type=float, help='Maximum duration to process in seconds')
    parser.add_argument('--max-frames', type=int, help='Maximum number of frames to process')
    parser.add_argument('--fps', type=float, help='Target FPS (will skip frames if needed)')
    parser.add_argument('--width', type=int, help='Target width')
    parser.add_argument('--height', type=int, help='Target height')
    parser.add_argument('--quality', type=int, default=85, help='JPEG quality (1-100)')
    parser.add_argument('--format', type=str, default='jpg', help='Output image format')
    parser.add_argument('--overwrite', action='store_true', help='Overwrite existing files')
    
    # Processing options
    parser.add_argument('--remove-background', action='store_true', help='Remove background from frames')
    parser.add_argument('--detect-objects', action='store_true', help='Detect objects in frames')
    
    args = parser.parse_args()
    
    # Create processor
    processor = VideoProcessor(output_dir=args.output, temp_dir=args.temp_dir)
    
    # Get target size if both width and height are provided
    target_size = None
    if args.width and args.height:
        target_size = (args.width, args.height)
    
    # Calculate duration from max_duration if provided
    duration = args.duration
    if args.max_duration:
        video_info = processor.get_video_info(args.video_path)
        duration = min(args.max_duration, video_info.duration - args.start_time)
    
    try:
        # Initialize processing
        if args.remove_background or args.detect_objects:
            print("Initializing processing modules...")
            processor.initialize_processing(
                remove_background=args.remove_background,
                detect_objects=args.detect_objects
            )
        
        # Extract and process frames
        print(f"Processing video: {args.video_path}")
        print(f"Output directory: {args.output}")
        if args.remove_background:
            print("- Background removal: ENABLED")
        if args.detect_objects:
            print("- Object detection: ENABLED")
        
        def progress_callback(progress, status):
            print(f"[PROGRESS] {int(progress * 100)}% - {status}")
        
        print("Extracting frames...")
        result = processor.extract_frames(
            video_path=args.video_path,
            output_dir=os.path.join(args.output, 'frames'),
            start_time=args.start_time,
            duration=duration,
            max_frames=args.max_frames,
            target_size=target_size,
            quality=args.quality,
            format=args.format,
            overwrite=args.overwrite,
            remove_background=args.remove_background,
            detect_objects=args.detect_objects,
            progress_callback=progress_callback
        )
        
        print(f"\nProcessing complete!")
        print(f"- Extracted {result['frame_count']} frames")
        print(f"- Output directory: {result['output_dir']}")
        print(f"- Metadata saved to: {result['metadata_path']}")
        
        return 0
        
    except Exception as e:
        import traceback
        print(f"Error: {e}", file=sys.stderr)
        print(traceback.format_exc(), file=sys.stderr)
        return 1
    
    return 0

if __name__ == '__main__':
    import sys
    sys.exit(main())
