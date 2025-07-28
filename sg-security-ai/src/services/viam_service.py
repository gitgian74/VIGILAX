import asyncio
import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import base64
from io import BytesIO

from viam.robot.client import RobotClient
from viam.components.camera import Camera
from viam.services.mlmodel import MLModelClient
from viam.services.vision import VisionClient
from viam.rpc.dial import DialOptions
from viam.media.video import CameraMimeType

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ViamService:
    """Service for managing VIAM robot connections and camera operations"""
    
    def __init__(self):
        self.robot_client: Optional[RobotClient] = None
        self.cameras: Dict[str, Camera] = {}
        self.vision_clients: Dict[str, VisionClient] = {}
        self.ml_model_clients: Dict[str, MLModelClient] = {}
        self.is_connected = False
        
        # Configuration from environment or defaults
        self.api_key = os.getenv('VIAM_API_KEY', '4mkomaqzmpne49vnhh43dz3wsq33or3r')
        self.api_key_id = os.getenv('VIAM_API_KEY_ID', '50ad7296-b4f5-4c75-8262-90f2cedc2f74')
        self.robot_address = os.getenv('VIAM_ROBOT_ADDRESS', 'ssa-locaratow-main.1j0se98dbn.viam.cloud')
        
    async def connect(self) -> bool:
        """Connect to VIAM robot"""
        try:
            opts = RobotClient.Options.with_api_key(
                api_key=self.api_key,
                api_key_id=self.api_key_id
            )
            
            self.robot_client = await RobotClient.at_address(self.robot_address, opts)
            
            logger.info("Connected to VIAM robot successfully")
            logger.info(f"Available resources: {self.robot_client.resource_names}")
            
            # Initialize cameras and services
            await self._initialize_components()
            
            self.is_connected = True
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to VIAM robot: {e}")
            self.is_connected = False
            return False
    
    async def disconnect(self):
        """Disconnect from VIAM robot"""
        try:
            if self.robot_client:
                await self.robot_client.close()
                self.robot_client = None
                self.cameras.clear()
                self.vision_clients.clear()
                self.ml_model_clients.clear()
                self.is_connected = False
                logger.info("Disconnected from VIAM robot")
        except Exception as e:
            logger.error(f"Error disconnecting from VIAM robot: {e}")
    
    async def _initialize_components(self):
        """Initialize cameras and services from robot"""
        if not self.robot_client:
            return
        
        try:
            # Get all resource names
            resources = self.robot_client.resource_names
            
            # Initialize cameras
            camera_names = ['camera-1', 'camera-2', 'video-store-camera-1', 'video-store-camera-2']
            
            for camera_name in camera_names:
                try:
                    camera = Camera.from_robot(self.robot_client, camera_name)
                    self.cameras[camera_name] = camera
                    logger.info(f"Initialized camera: {camera_name}")
                except Exception as e:
                    logger.warning(f"Could not initialize camera {camera_name}: {e}")
            
            # Initialize vision services
            try:
                vision_client = VisionClient.from_robot(self.robot_client, "vision-1")
                self.vision_clients["vision-1"] = vision_client
                logger.info("Initialized vision service: vision-1")
            except Exception as e:
                logger.warning(f"Could not initialize vision service: {e}")
            
            # Initialize ML model services
            try:
                ml_client = MLModelClient.from_robot(self.robot_client, "ml_model_service")
                self.ml_model_clients["ml_model_service"] = ml_client
                logger.info("Initialized ML model service: ml_model_service")
            except Exception as e:
                logger.warning(f"Could not initialize ML model service: {e}")
                
        except Exception as e:
            logger.error(f"Error initializing components: {e}")
    
    async def get_camera_image(self, camera_id: str, mime_type: str = "JPEG") -> Optional[bytes]:
        """Get image from camera"""
        if not self.is_connected or camera_id not in self.cameras:
            logger.error(f"Camera {camera_id} not available")
            return None
        
        try:
            camera = self.cameras[camera_id]
            
            # Convert mime type string to enum
            if mime_type.upper() == "JPEG":
                mime_enum = CameraMimeType.JPEG
            elif mime_type.upper() == "PNG":
                mime_enum = CameraMimeType.PNG
            else:
                mime_enum = CameraMimeType.JPEG
            
            image = await camera.get_image(mime_enum)
            return image
            
        except Exception as e:
            logger.error(f"Error getting image from camera {camera_id}: {e}")
            return None
    
    async def get_camera_image_base64(self, camera_id: str) -> Optional[str]:
        """Get camera image as base64 string"""
        image_bytes = await self.get_camera_image(camera_id)
        if image_bytes:
            return base64.b64encode(image_bytes).decode('utf-8')
        return None
    
    async def detect_objects(self, camera_id: str, vision_service: str = "vision-1") -> List[Dict[str, Any]]:
        """Detect objects in camera image using vision service"""
        if not self.is_connected or vision_service not in self.vision_clients:
            logger.error(f"Vision service {vision_service} not available")
            return []
        
        try:
            # Get image from camera
            image_bytes = await self.get_camera_image(camera_id)
            if not image_bytes:
                return []
            
            # Use vision service for detection
            vision_client = self.vision_clients[vision_service]
            
            # Get detections from camera directly
            if camera_id in self.cameras:
                detections = await vision_client.get_detections_from_camera(camera_id, "detector_1")
                
                results = []
                for detection in detections:
                    results.append({
                        'class_name': detection.class_name,
                        'confidence': detection.confidence,
                        'x_min': detection.x_min,
                        'y_min': detection.y_min,
                        'x_max': detection.x_max,
                        'y_max': detection.y_max
                    })
                
                return results
            
        except Exception as e:
            logger.error(f"Error detecting objects in camera {camera_id}: {e}")
            return []
    
    async def run_ml_inference(self, camera_id: str, model_service: str = "ml_model_service") -> Dict[str, Any]:
        """Run ML model inference on camera image"""
        if not self.is_connected or model_service not in self.ml_model_clients:
            logger.error(f"ML model service {model_service} not available")
            return {}
        
        try:
            # Get image from camera
            image_bytes = await self.get_camera_image(camera_id)
            if not image_bytes:
                return {}
            
            # Use ML model service for inference
            ml_client = self.ml_model_clients[model_service]
            
            # Get model metadata
            metadata = await ml_client.metadata()
            logger.info(f"ML model metadata: {metadata}")
            
            # TODO: Implement actual inference call
            # This would depend on the specific model and its input/output format
            
            return {
                'model_metadata': metadata,
                'inference_result': 'placeholder',
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error running ML inference for camera {camera_id}: {e}")
            return {}
    
    async def get_camera_status(self, camera_id: str) -> Dict[str, Any]:
        """Get camera status and health information"""
        if not self.is_connected:
            return {
                'camera_id': camera_id,
                'status': 'disconnected',
                'error': 'VIAM robot not connected'
            }
        
        if camera_id not in self.cameras:
            return {
                'camera_id': camera_id,
                'status': 'not_found',
                'error': f'Camera {camera_id} not found'
            }
        
        try:
            # Try to get an image to test camera health
            image_bytes = await self.get_camera_image(camera_id)
            
            status = {
                'camera_id': camera_id,
                'status': 'online' if image_bytes else 'offline',
                'last_check': datetime.utcnow().isoformat(),
                'image_available': bool(image_bytes)
            }
            
            if image_bytes:
                status['image_size_bytes'] = len(image_bytes)
            
            return status
            
        except Exception as e:
            return {
                'camera_id': camera_id,
                'status': 'error',
                'error': str(e),
                'last_check': datetime.utcnow().isoformat()
            }
    
    async def get_all_cameras_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status for all cameras"""
        status_dict = {}
        
        for camera_id in self.cameras.keys():
            status_dict[camera_id] = await self.get_camera_status(camera_id)
        
        return status_dict
    
    def get_available_cameras(self) -> List[str]:
        """Get list of available camera IDs"""
        return list(self.cameras.keys())
    
    def get_connection_status(self) -> Dict[str, Any]:
        """Get overall connection status"""
        return {
            'connected': self.is_connected,
            'robot_address': self.robot_address,
            'available_cameras': len(self.cameras),
            'available_vision_services': len(self.vision_clients),
            'available_ml_services': len(self.ml_model_clients),
            'last_check': datetime.utcnow().isoformat()
        }

# Global VIAM service instance
viam_service = ViamService()

async def initialize_viam_service() -> bool:
    """Initialize the global VIAM service"""
    return await viam_service.connect()

async def shutdown_viam_service():
    """Shutdown the global VIAM service"""
    await viam_service.disconnect()

# Convenience functions for use in Flask routes
def get_viam_service() -> ViamService:
    """Get the global VIAM service instance"""
    return viam_service

async def ensure_viam_connection() -> bool:
    """Ensure VIAM service is connected"""
    if not viam_service.is_connected:
        return await viam_service.connect()
    return True

