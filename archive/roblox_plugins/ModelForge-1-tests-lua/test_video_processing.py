"""
Test script for video processing functionality.
"""

import os
import sys
import unittest
import tempfile
import shutil
import cv2
import numpy as np
import json
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add the scripts directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))
from video_processor import VideoProcessor, VideoInfo

class TestVideoProcessing(unittest.TestCase):    
    @classmethod
    def setUpClass(cls):
        """Set up test environment before any tests run."""
        # Create a temporary directory for test outputs
        cls.test_dir = Path(tempfile.mkdtemp(prefix='test_video_processor_'))
        cls.output_dir = cls.test_dir / 'output'
        cls.temp_dir = cls.test_dir / 'temp'
        
        # Create test directories
        os.makedirs(cls.output_dir, exist_ok=True)
        os.makedirs(cls.temp_dir, exist_ok=True)
        
        # Create test videos
        cls.test_video_path = cls._create_test_video()
        
        # Initialize video processor
        cls.processor = VideoProcessor(
            output_dir=str(cls.output_dir),
            temp_dir=str(cls.temp_dir)
        )
    
    @classmethod
    def tearDownClass(cls):
        """Clean up after all tests have run."""
        shutil.rmtree(cls.test_dir, ignore_errors=True)
    
    @classmethod
    def _create_test_video(cls, duration: float = 5.0, fps: int = 30, 
                          width: int = 640, height: int = 480) -> str:
        """Create a simple test video with moving patterns."""
        video_path = str(cls.test_dir / 'test_video.mp4')
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(video_path, fourcc, fps, (width, height))
        
        try:
            for i in range(int(duration * fps)):
                # Create a frame with a moving pattern
                frame = np.zeros((height, width, 3), dtype=np.uint8)
                
                # Draw a moving rectangle
                pos = int((i / (duration * fps)) * (width - 100))
                cv2.rectangle(frame, (pos, 50), (pos + 100, 150), (0, 255, 0), -1)
                
                # Draw some text
                cv2.putText(frame, f'Frame {i}', (50, 50), 
                          cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                
                out.write(frame)
        finally:
            out.release()
        
        return video_path
    
    def test_video_info(self):
        """Test video information extraction."""
        info = self.processor.get_video_info(self.test_video_path)
        
        self.assertIsInstance(info, VideoInfo)
        self.assertEqual(info.width, 640)
        self.assertEqual(info.height, 480)
        self.assertGreater(info.fps, 0)
        self.assertGreater(info.frame_count, 0)
        self.assertGreater(info.duration, 0)
    
    def test_extract_frames(self):
        """Test frame extraction from video."""
        # Extract frames with default settings
        frames = self.processor.extract_frames(
            self.test_video_path,
            max_frames=10,
            target_size=(320, 240)
        )
        
        # Verify results
        self.assertEqual(len(frames), 10)
        self.assertTrue(all(os.path.exists(f) for f in frames))
        
        # Check frame dimensions
        img = cv2.imread(frames[0])
        self.assertEqual(img.shape[:2], (240, 320))  # (height, width)
    
    def test_extract_audio(self):
        """Test audio extraction from video."""
        # Our test video doesn't have audio, so this should return None
        audio_path = self.processor.extract_audio(self.test_video_path)
        self.assertIsNone(audio_path)
    
    def test_process_video_for_3d(self):
        """Test the complete video processing pipeline."""
        output_dir = str(self.output_dir / 'processed_video')
        
        # Process the video
        result = self.processor.process_video_for_3d(
            video_path=self.test_video_path,
            output_dir=output_dir,
            max_duration=2.0,  # Only process 2 seconds
            target_fps=15,     # Lower FPS for testing
            target_size=(512, 512)
        )
        
        # Verify results
        self.assertIn('video_info', result)
        self.assertIn('processing', result)
        self.assertGreater(result['processing']['frames_extracted'], 0)
        self.assertLessEqual(result['processing']['duration_processed'], 2.0)
        
        # Check that frames were extracted
        self.assertTrue(os.path.isdir(os.path.join(output_dir, 'frames')))
        self.assertGreater(len(os.listdir(os.path.join(output_dir, 'frames'))), 0)
        
        # Check processing info file
        info_path = os.path.join(output_dir, 'processing_info.json')
        self.assertTrue(os.path.exists(info_path))
    
    def test_invalid_video_path(self):
        """Test behavior with invalid video path."""
        with self.assertRaises(FileNotFoundError):
            self.processor.get_video_info('nonexistent_video.mp4')
        
        with self.assertRaises(FileNotFoundError):
            self.processor.extract_frames('nonexistent_video.mp4')


class TestBackgroundRemovalAndObjectDetection(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test environment before any tests run."""
        # Create a temporary directory for test outputs
        cls.test_dir = Path(tempfile.mkdtemp(prefix='test_bg_removal_'))
        cls.output_dir = cls.test_dir / 'output'
        
        # Create test directories
        os.makedirs(cls.output_dir, exist_ok=True)
        
        # Create a test video with a simple scene
        cls.test_video_path = cls._create_test_video_with_objects()
        
        # Initialize video processor
        cls.processor = VideoProcessor(output_dir=str(cls.output_dir))
    
    @classmethod
    def tearDownClass(cls):
        """Clean up after all tests have run."""
        shutil.rmtree(cls.test_dir, ignore_errors=True)
    
    @classmethod
    def _create_test_video_with_objects(cls, duration: float = 3.0, fps: int = 10, 
                                      width: int = 320, height: int = 240) -> str:
        """Create a test video with simple objects for detection testing."""
        video_path = str(cls.test_dir / 'test_objects.mp4')
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(video_path, fourcc, fps, (width, height))
        
        try:
            for i in range(int(duration * fps)):
                # Create a frame with a colored background
                frame = np.full((height, width, 3), (100, 100, 200), dtype=np.uint8)
                
                # Draw a colored rectangle (simulated object)
                if i % 2 == 0:
                    color = (0, 255, 0)  # Green
                else:
                    color = (0, 0, 255)  # Red
                
                # Draw a moving object
                pos = int((i / (duration * fps)) * (width - 60))
                cv2.rectangle(frame, (pos, 50), (pos + 60, 150), color, -1)
                
                # Add some noise to make it more realistic
                noise = np.random.normal(0, 10, frame.shape).astype(np.uint8)
                frame = cv2.add(frame, noise)
                
                out.write(frame)
        finally:
            out.release()
        
        return video_path
    
    def test_background_removal(self):
        """Test background removal functionality."""
        # Initialize the processor with background removal
        self.processor.initialize_processing(
            remove_background=True,
            detect_objects=False,
            bg_method='MOG2',
            bg_history=100,
            bg_var_threshold=16
        )
        
        # Create a test output directory
        output_dir = os.path.join(self.output_dir, 'test_bg_removal')
        os.makedirs(output_dir, exist_ok=True)
        
        # Process the video with background removal
        result = self.processor.extract_frames(
            video_path=self.test_video_path,
            output_dir=output_dir,
            max_frames=5,
            remove_background=True,
            target_size=(320, 240)
        )
        
        # Verify results
        self.assertIn('frame_paths', result)
        self.assertIn('metadata_path', result)
        self.assertEqual(len(result['frame_paths']), 5)
        
        # Load metadata
        with open(result['metadata_path'], 'r') as f:
            metadata = json.load(f)
        
        # Check that metadata contains processing info
        self.assertIn('processing_options', metadata)
        self.assertTrue(metadata['processing_options']['remove_background'])
        
        # Check that frames were processed
        for frame_path in result['frame_paths']:
            self.assertTrue(os.path.exists(frame_path), f"Frame {frame_path} does not exist")
            img = cv2.imread(frame_path, cv2.IMREAD_UNCHANGED)
            self.assertIsNotNone(img, f"Failed to load image: {frame_path}")
            if img is not None:
                self.assertEqual(img.shape[:2], (240, 320))  # (height, width)
    
    @patch('video_processor.cv2.dnn_DetectionModel')
    def test_object_detection(self, mock_detection_model):
        """Test object detection functionality with mock model."""
        from unittest.mock import MagicMock, ANY
        
        # Create a test output directory
        output_dir = os.path.join(self.output_dir, 'test_object_detection')
        os.makedirs(output_dir, exist_ok=True)
        
        # Create a mock detection model
        mock_model = MagicMock()
        mock_detection_model.return_value = mock_model
        
        # Create a mock detection result
        class MockDetection:
            def __init__(self, class_name, confidence, bbox):
                self.class_name = class_name
                self.confidence = confidence
                self.bbox = bbox
                
            def to_dict(self):
                return {
                    'class_name': self.class_name,
                    'confidence': self.confidence,
                    'bbox': self.bbox
                }
        
        # Mock the object detector
        self.processor.object_detector = MagicMock()
        self.processor.object_detector.detect.return_value = [
            MockDetection('object', 0.95, [10, 20, 100, 150])
        ]
        self.processor.object_detector.confidence_threshold = 0.5
        
        # Process the video with object detection
        result = self.processor.extract_frames(
            video_path=self.test_video_path,
            output_dir=output_dir,
            max_frames=3,
            detect_objects=True,
            target_size=(320, 240)
        )
        
        # Verify results
        self.assertIn('frame_paths', result)
        self.assertIn('metadata_path', result)
        self.assertEqual(len(result['frame_paths']), 3)
        
        # Verify the object detector was called
        self.processor.object_detector.detect.assert_called()
        
        # Load metadata
        with open(result['metadata_path'], 'r') as f:
            metadata = json.load(f)
        
        # Check that metadata contains detection info
        self.assertIn('frame_metadata', metadata)
        self.assertGreater(len(metadata['frame_metadata']), 0)
        self.assertEqual(metadata['frame_metadata'][0]['objects'][0]['class'], 'object')
        self.assertGreaterEqual(metadata['frame_metadata'][0]['objects'][0]['confidence'], 0.5)
    
    def test_combined_processing(self):
        """Test combined background removal and object detection."""
        # Create a test output directory
        output_dir = os.path.join(self.output_dir, 'test_combined_processing')
        os.makedirs(output_dir, exist_ok=True)
        
        # Initialize the processor with both features
        self.processor.initialize_processing(
            remove_background=True,
            detect_objects=True,
            bg_method='MOG2',
            confidence_threshold=0.5
        )
        
        # Mock object detector
        self.processor.object_detector = MagicMock()
        self.processor.object_detector.detect.return_value = [
            MagicMock(class_name='object', confidence=0.9, bbox=(10, 20, 100, 150))
        ]
        
        # Process the video with both features
        result = self.processor.extract_frames(
            video_path=self.test_video_path,
            output_dir=output_dir,
            max_frames=3,
            remove_background=True,
            detect_objects=True,
            target_size=(320, 240)
        )
        
        # Verify results
        self.assertIn('frame_paths', result)
        self.assertEqual(len(result['frame_paths']), 3)
        
        # Load metadata
        with open(result['metadata_path'], 'r') as f:
            metadata = json.load(f)
        
        # Check that both features were applied
        self.assertTrue(metadata['processing_options']['remove_background'])
        self.assertTrue(metadata['processing_options']['detect_objects'])
        
        # Check that frames were processed
        for frame_path in result['frame_paths']:
            self.assertTrue(os.path.exists(frame_path), f"Frame {frame_path} does not exist")

if __name__ == '__main__':
    unittest.main()
