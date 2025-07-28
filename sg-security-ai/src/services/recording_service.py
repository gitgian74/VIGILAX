import os
import asyncio
import threading
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json
import cv2
import numpy as np
from pathlib import Path

from src.services.viam_service import get_viam_service
from src.models.user import Recording, db
from src.models.camera import Camera, SystemConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RecordingService:
    """Service for managing local video recordings"""
    
    def __init__(self):
        self.recording_sessions: Dict[str, Dict] = {}
        self.recording_threads: Dict[str, threading.Thread] = {}
        self.stop_events: Dict[str, threading.Event] = {}
        
        # Configuration
        self.base_recording_path = '/home/ubuntu/recordings'
        self.max_recording_size_gb = 100
        self.retention_days = 30
        self.recording_fps = 10  # FPS for recordings
        self.segment_duration_minutes = 30  # Split recordings into segments
        
        # Ensure recording directories exist
        self._setup_recording_directories()
        
        # Load configuration from database
        self._load_configuration()
    
    def _setup_recording_directories(self):
        """Create necessary recording directories"""
        try:
            directories = [
                self.base_recording_path,
                os.path.join(self.base_recording_path, 'videos'),
                os.path.join(self.base_recording_path, 'snapshots'),
                os.path.join(self.base_recording_path, 'temp'),
                os.path.join(self.base_recording_path, 'ai_events')
            ]
            
            for directory in directories:
                os.makedirs(directory, exist_ok=True)
                logger.info(f"Created/verified directory: {directory}")
                
        except Exception as e:
            logger.error(f"Error setting up recording directories: {e}")
    
    def _load_configuration(self):
        """Load configuration from database"""
        try:
            # Get recording path
            path_config = SystemConfig.query.filter_by(key='recording_path').first()
            if path_config:
                self.base_recording_path = path_config.get_value()
            
            # Get max size
            size_config = SystemConfig.query.filter_by(key='max_recording_size_gb').first()
            if size_config:
                self.max_recording_size_gb = int(size_config.get_value())
            
            # Get retention days
            retention_config = SystemConfig.query.filter_by(key='retention_days').first()
            if retention_config:
                self.retention_days = int(retention_config.get_value())
                
            logger.info(f"Loaded recording configuration: path={self.base_recording_path}, "
                       f"max_size={self.max_recording_size_gb}GB, retention={self.retention_days}days")
                       
        except Exception as e:
            logger.error(f"Error loading recording configuration: {e}")
    
    def start_recording(self, camera_id: str, user_id: int, duration_minutes: Optional[int] = None) -> Dict[str, Any]:
        """Start recording from a camera"""
        try:
            # Check if already recording
            if camera_id in self.recording_sessions:
                return {
                    'success': False,
                    'error': f'Camera {camera_id} is already being recorded'
                }
            
            # Check camera exists and is enabled for recording
            camera = Camera.query.get(camera_id)
            if not camera:
                return {
                    'success': False,
                    'error': f'Camera {camera_id} not found'
                }
            
            if not camera.recording_enabled:
                return {
                    'success': False,
                    'error': f'Recording is disabled for camera {camera_id}'
                }
            
            # Check available space
            if not self._check_available_space():
                return {
                    'success': False,
                    'error': 'Insufficient storage space for recording'
                }
            
            # Create recording session
            session_id = f"{camera_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            
            # Create recording record in database
            recording = Recording(
                camera_id=camera_id,
                user_id=user_id,
                filename='',  # Will be set when recording starts
                file_path='',  # Will be set when recording starts
                duration=0,
                file_size=0,
                recording_type='manual' if duration_minutes else 'continuous',
                metadata=json.dumps({
                    'session_id': session_id,
                    'requested_duration': duration_minutes,
                    'fps': self.recording_fps
                })
            )
            
            db.session.add(recording)
            db.session.commit()
            
            # Setup recording session
            self.recording_sessions[camera_id] = {
                'session_id': session_id,
                'recording_id': recording.id,
                'camera_id': camera_id,
                'user_id': user_id,
                'start_time': datetime.utcnow(),
                'duration_minutes': duration_minutes,
                'current_segment': 1,
                'total_frames': 0,
                'total_size_bytes': 0
            }
            
            # Create stop event
            self.stop_events[camera_id] = threading.Event()
            
            # Start recording thread
            recording_thread = threading.Thread(
                target=self._recording_worker,
                args=(camera_id,),
                daemon=True
            )
            
            self.recording_threads[camera_id] = recording_thread
            recording_thread.start()
            
            logger.info(f"Started recording for camera {camera_id}, session {session_id}")
            
            return {
                'success': True,
                'session_id': session_id,
                'recording_id': recording.id,
                'message': f'Recording started for camera {camera_id}'
            }
            
        except Exception as e:
            logger.error(f"Error starting recording for camera {camera_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def stop_recording(self, camera_id: str) -> Dict[str, Any]:
        """Stop recording for a camera"""
        try:
            if camera_id not in self.recording_sessions:
                return {
                    'success': False,
                    'error': f'No active recording for camera {camera_id}'
                }
            
            # Signal stop
            if camera_id in self.stop_events:
                self.stop_events[camera_id].set()
            
            # Wait for thread to finish
            if camera_id in self.recording_threads:
                self.recording_threads[camera_id].join(timeout=10)
            
            session = self.recording_sessions.get(camera_id, {})
            session_id = session.get('session_id', 'unknown')
            
            # Clean up
            self._cleanup_recording_session(camera_id)
            
            logger.info(f"Stopped recording for camera {camera_id}, session {session_id}")
            
            return {
                'success': True,
                'session_id': session_id,
                'message': f'Recording stopped for camera {camera_id}'
            }
            
        except Exception as e:
            logger.error(f"Error stopping recording for camera {camera_id}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _recording_worker(self, camera_id: str):
        """Worker thread for recording video from camera"""
        session = self.recording_sessions.get(camera_id)
        if not session:
            return
        
        try:
            viam_service = get_viam_service()
            
            # Create video writer
            video_writer = None
            current_filename = None
            current_filepath = None
            segment_start_time = datetime.utcnow()
            
            frame_count = 0
            total_size = 0
            
            while not self.stop_events[camera_id].is_set():
                try:
                    # Check if we need to start a new segment
                    if (video_writer is None or 
                        (datetime.utcnow() - segment_start_time).total_seconds() > self.segment_duration_minutes * 60):
                        
                        # Close previous writer
                        if video_writer:
                            video_writer.release()
                            self._finalize_recording_segment(camera_id, current_filepath, frame_count, total_size)
                        
                        # Create new segment
                        current_filename, current_filepath, video_writer = self._create_new_segment(camera_id, session)
                        segment_start_time = datetime.utcnow()
                        frame_count = 0
                    
                    # Get frame from camera
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    frame_bytes = loop.run_until_complete(viam_service.get_camera_image(camera_id, 'JPEG'))
                    loop.close()
                    
                    if frame_bytes and video_writer:
                        # Convert bytes to OpenCV image
                        nparr = np.frombuffer(frame_bytes, np.uint8)
                        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                        
                        if frame is not None:
                            # Write frame to video
                            video_writer.write(frame)
                            frame_count += 1
                            total_size += len(frame_bytes)
                            
                            # Update session stats
                            session['total_frames'] += 1
                            session['total_size_bytes'] += len(frame_bytes)
                    
                    # Check duration limit
                    if session.get('duration_minutes'):
                        elapsed_minutes = (datetime.utcnow() - session['start_time']).total_seconds() / 60
                        if elapsed_minutes >= session['duration_minutes']:
                            break
                    
                    # Sleep to maintain FPS
                    time.sleep(1.0 / self.recording_fps)
                    
                except Exception as e:
                    logger.error(f"Error in recording loop for camera {camera_id}: {e}")
                    time.sleep(1)
            
            # Finalize last segment
            if video_writer:
                video_writer.release()
                self._finalize_recording_segment(camera_id, current_filepath, frame_count, total_size)
            
            # Update recording record
            self._finalize_recording_session(camera_id)
            
        except Exception as e:
            logger.error(f"Error in recording worker for camera {camera_id}: {e}")
        finally:
            self._cleanup_recording_session(camera_id)
    
    def _create_new_segment(self, camera_id: str, session: Dict) -> tuple:
        """Create a new video segment"""
        try:
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            segment_num = session['current_segment']
            
            filename = f"{camera_id}_segment_{segment_num:03d}_{timestamp}.mp4"
            filepath = os.path.join(self.base_recording_path, 'videos', filename)
            
            # Create video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            video_writer = cv2.VideoWriter(filepath, fourcc, self.recording_fps, (1920, 1080))
            
            if not video_writer.isOpened():
                raise Exception(f"Could not create video writer for {filepath}")
            
            session['current_segment'] += 1
            
            logger.info(f"Created new recording segment: {filename}")
            
            return filename, filepath, video_writer
            
        except Exception as e:
            logger.error(f"Error creating new segment for camera {camera_id}: {e}")
            raise
    
    def _finalize_recording_segment(self, camera_id: str, filepath: str, frame_count: int, size_bytes: int):
        """Finalize a recording segment"""
        try:
            if not os.path.exists(filepath):
                return
            
            # Get actual file size
            actual_size = os.path.getsize(filepath)
            
            logger.info(f"Finalized recording segment: {filepath}, "
                       f"frames={frame_count}, size={actual_size} bytes")
            
        except Exception as e:
            logger.error(f"Error finalizing recording segment {filepath}: {e}")
    
    def _finalize_recording_session(self, camera_id: str):
        """Finalize the entire recording session"""
        try:
            session = self.recording_sessions.get(camera_id)
            if not session:
                return
            
            # Update recording record in database
            recording = Recording.query.get(session['recording_id'])
            if recording:
                duration_seconds = (datetime.utcnow() - session['start_time']).total_seconds()
                recording.duration = int(duration_seconds)
                recording.file_size = session['total_size_bytes']
                recording.ended_at = datetime.utcnow()
                
                # Update metadata
                metadata = json.loads(recording.metadata or '{}')
                metadata.update({
                    'total_frames': session['total_frames'],
                    'segments': session['current_segment'] - 1,
                    'actual_fps': session['total_frames'] / duration_seconds if duration_seconds > 0 else 0
                })
                recording.metadata = json.dumps(metadata)
                
                db.session.commit()
                
                logger.info(f"Finalized recording session for camera {camera_id}, "
                           f"duration={duration_seconds}s, frames={session['total_frames']}")
            
        except Exception as e:
            logger.error(f"Error finalizing recording session for camera {camera_id}: {e}")
    
    def _cleanup_recording_session(self, camera_id: str):
        """Clean up recording session data"""
        try:
            # Remove from active sessions
            if camera_id in self.recording_sessions:
                del self.recording_sessions[camera_id]
            
            # Clean up thread references
            if camera_id in self.recording_threads:
                del self.recording_threads[camera_id]
            
            # Clean up stop events
            if camera_id in self.stop_events:
                del self.stop_events[camera_id]
                
        except Exception as e:
            logger.error(f"Error cleaning up recording session for camera {camera_id}: {e}")
    
    def _check_available_space(self) -> bool:
        """Check if there's enough space for recording"""
        try:
            # Get disk usage
            statvfs = os.statvfs(self.base_recording_path)
            free_bytes = statvfs.f_frsize * statvfs.f_bavail
            free_gb = free_bytes / (1024**3)
            
            # Check if we have at least 10% of max recording size available
            required_gb = self.max_recording_size_gb * 0.1
            
            return free_gb >= required_gb
            
        except Exception as e:
            logger.error(f"Error checking available space: {e}")
            return False
    
    def get_active_recordings(self) -> List[Dict[str, Any]]:
        """Get list of active recordings"""
        active_recordings = []
        
        for camera_id, session in self.recording_sessions.items():
            duration_seconds = (datetime.utcnow() - session['start_time']).total_seconds()
            
            active_recordings.append({
                'camera_id': camera_id,
                'session_id': session['session_id'],
                'recording_id': session['recording_id'],
                'user_id': session['user_id'],
                'start_time': session['start_time'].isoformat(),
                'duration_seconds': int(duration_seconds),
                'current_segment': session['current_segment'],
                'total_frames': session['total_frames'],
                'total_size_bytes': session['total_size_bytes']
            })
        
        return active_recordings
    
    def get_recording_statistics(self) -> Dict[str, Any]:
        """Get recording statistics"""
        try:
            # Count recordings by type
            total_recordings = Recording.query.count()
            manual_recordings = Recording.query.filter_by(recording_type='manual').count()
            continuous_recordings = Recording.query.filter_by(recording_type='continuous').count()
            
            # Calculate total storage used
            total_size = db.session.query(db.func.sum(Recording.file_size)).scalar() or 0
            total_duration = db.session.query(db.func.sum(Recording.duration)).scalar() or 0
            
            # Get disk usage
            statvfs = os.statvfs(self.base_recording_path)
            free_bytes = statvfs.f_frsize * statvfs.f_bavail
            total_bytes = statvfs.f_frsize * statvfs.f_blocks
            used_bytes = total_bytes - free_bytes
            
            return {
                'total_recordings': total_recordings,
                'manual_recordings': manual_recordings,
                'continuous_recordings': continuous_recordings,
                'active_recordings': len(self.recording_sessions),
                'total_recorded_size_bytes': total_size,
                'total_recorded_duration_seconds': total_duration,
                'disk_usage': {
                    'total_bytes': total_bytes,
                    'used_bytes': used_bytes,
                    'free_bytes': free_bytes,
                    'used_percentage': (used_bytes / total_bytes) * 100 if total_bytes > 0 else 0
                },
                'configuration': {
                    'base_path': self.base_recording_path,
                    'max_size_gb': self.max_recording_size_gb,
                    'retention_days': self.retention_days,
                    'recording_fps': self.recording_fps,
                    'segment_duration_minutes': self.segment_duration_minutes
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting recording statistics: {e}")
            return {}
    
    def cleanup_old_recordings(self) -> Dict[str, Any]:
        """Clean up old recordings based on retention policy"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=self.retention_days)
            
            # Find old recordings
            old_recordings = Recording.query.filter(Recording.created_at < cutoff_date).all()
            
            deleted_count = 0
            freed_bytes = 0
            
            for recording in old_recordings:
                try:
                    # Delete file if it exists
                    if recording.file_path and os.path.exists(recording.file_path):
                        file_size = os.path.getsize(recording.file_path)
                        os.remove(recording.file_path)
                        freed_bytes += file_size
                    
                    # Delete database record
                    db.session.delete(recording)
                    deleted_count += 1
                    
                except Exception as e:
                    logger.error(f"Error deleting recording {recording.id}: {e}")
            
            db.session.commit()
            
            logger.info(f"Cleaned up {deleted_count} old recordings, freed {freed_bytes} bytes")
            
            return {
                'success': True,
                'deleted_recordings': deleted_count,
                'freed_bytes': freed_bytes,
                'cutoff_date': cutoff_date.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error cleaning up old recordings: {e}")
            return {
                'success': False,
                'error': str(e)
            }

# Global recording service instance
recording_service = RecordingService()

def get_recording_service() -> RecordingService:
    """Get the global recording service instance"""
    return recording_service

