from flask import Blueprint, jsonify, request, Response
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
import asyncio
import json
from datetime import datetime

from src.models.user import User
from src.models.camera import Camera, StreamSession, db
from src.services.viam_service import get_viam_service, ensure_viam_connection

viam_bp = Blueprint('viam', __name__)

def require_role(allowed_roles):
    """Decorator to require specific roles"""
    def decorator(f):
        def wrapper(*args, **kwargs):
            claims = get_jwt()
            user_role = claims.get('role')
            
            if user_role not in allowed_roles:
                return jsonify({'error': 'Insufficient permissions'}), 403
            
            return f(*args, **kwargs)
        wrapper.__name__ = f.__name__
        return wrapper
    return decorator

def check_camera_access(user, camera_id):
    """Check if user has access to specific camera"""
    if user.role in ['super_admin', 'admin']:
        return True
    return camera_id in user.get_assigned_cameras()

@viam_bp.route('/viam/status', methods=['GET'])
@jwt_required()
def get_viam_status():
    """Get VIAM connection status"""
    try:
        viam_service = get_viam_service()
        status = viam_service.get_connection_status()
        return jsonify({'status': status})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@viam_bp.route('/viam/connect', methods=['POST'])
@jwt_required()
@require_role(['super_admin', 'admin'])
def connect_viam():
    """Connect to VIAM robot"""
    try:
        async def _connect():
            return await ensure_viam_connection()
        
        # Run async function in event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        success = loop.run_until_complete(_connect())
        loop.close()
        
        if success:
            return jsonify({'message': 'Connected to VIAM robot successfully'})
        else:
            return jsonify({'error': 'Failed to connect to VIAM robot'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@viam_bp.route('/viam/disconnect', methods=['POST'])
@jwt_required()
@require_role(['super_admin', 'admin'])
def disconnect_viam():
    """Disconnect from VIAM robot"""
    try:
        async def _disconnect():
            viam_service = get_viam_service()
            await viam_service.disconnect()
        
        # Run async function in event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(_disconnect())
        loop.close()
        
        return jsonify({'message': 'Disconnected from VIAM robot'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@viam_bp.route('/viam/cameras', methods=['GET'])
@jwt_required()
def get_viam_cameras():
    """Get available VIAM cameras"""
    try:
        viam_service = get_viam_service()
        cameras = viam_service.get_available_cameras()
        
        return jsonify({
            'cameras': cameras,
            'total': len(cameras),
            'connected': viam_service.is_connected
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@viam_bp.route('/viam/cameras/status', methods=['GET'])
@jwt_required()
def get_all_cameras_viam_status():
    """Get status for all VIAM cameras"""
    try:
        async def _get_status():
            viam_service = get_viam_service()
            return await viam_service.get_all_cameras_status()
        
        # Run async function in event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        status = loop.run_until_complete(_get_status())
        loop.close()
        
        return jsonify({'cameras_status': status})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@viam_bp.route('/viam/cameras/<camera_id>/status', methods=['GET'])
@jwt_required()
def get_camera_viam_status(camera_id):
    """Get VIAM status for specific camera"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Check access permissions
        if not check_camera_access(user, camera_id):
            return jsonify({'error': 'Access denied to this camera'}), 403
        
        async def _get_status():
            viam_service = get_viam_service()
            return await viam_service.get_camera_status(camera_id)
        
        # Run async function in event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        status = loop.run_until_complete(_get_status())
        loop.close()
        
        return jsonify({'camera_status': status})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@viam_bp.route('/viam/cameras/<camera_id>/image', methods=['GET'])
@jwt_required()
def get_camera_image(camera_id):
    """Get image from VIAM camera"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Check access permissions
        if not check_camera_access(user, camera_id):
            return jsonify({'error': 'Access denied to this camera'}), 403
        
        # Get format from query parameters
        format_type = request.args.get('format', 'base64')
        mime_type = request.args.get('mime', 'JPEG')
        
        async def _get_image():
            viam_service = get_viam_service()
            if format_type == 'base64':
                return await viam_service.get_camera_image_base64(camera_id)
            else:
                return await viam_service.get_camera_image(camera_id, mime_type)
        
        # Run async function in event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        image_data = loop.run_until_complete(_get_image())
        loop.close()
        
        if not image_data:
            return jsonify({'error': 'Failed to get image from camera'}), 500
        
        if format_type == 'base64':
            return jsonify({
                'camera_id': camera_id,
                'image_base64': image_data,
                'mime_type': mime_type,
                'timestamp': datetime.utcnow().isoformat()
            })
        else:
            # Return raw image data
            return Response(
                image_data,
                mimetype=f'image/{mime_type.lower()}',
                headers={
                    'Content-Disposition': f'inline; filename="{camera_id}_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.{mime_type.lower()}"'
                }
            )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@viam_bp.route('/viam/cameras/<camera_id>/detect', methods=['POST'])
@jwt_required()
def detect_objects_in_camera(camera_id):
    """Detect objects in camera image using VIAM vision service"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Check access permissions
        if not check_camera_access(user, camera_id):
            return jsonify({'error': 'Access denied to this camera'}), 403
        
        # Get vision service from request
        data = request.get_json() or {}
        vision_service = data.get('vision_service', 'vision-1')
        
        async def _detect():
            viam_service = get_viam_service()
            return await viam_service.detect_objects(camera_id, vision_service)
        
        # Run async function in event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        detections = loop.run_until_complete(_detect())
        loop.close()
        
        return jsonify({
            'camera_id': camera_id,
            'detections': detections,
            'detection_count': len(detections),
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@viam_bp.route('/viam/cameras/<camera_id>/inference', methods=['POST'])
@jwt_required()
def run_ml_inference_on_camera(camera_id):
    """Run ML model inference on camera image"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Check access permissions
        if not check_camera_access(user, camera_id):
            return jsonify({'error': 'Access denied to this camera'}), 403
        
        # Get ML service from request
        data = request.get_json() or {}
        ml_service = data.get('ml_service', 'ml_model_service')
        
        async def _inference():
            viam_service = get_viam_service()
            return await viam_service.run_ml_inference(camera_id, ml_service)
        
        # Run async function in event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(_inference())
        loop.close()
        
        return jsonify({
            'camera_id': camera_id,
            'inference_result': result,
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@viam_bp.route('/viam/cameras/<camera_id>/stream', methods=['GET'])
@jwt_required()
def stream_camera_mjpeg(camera_id):
    """Stream camera images as MJPEG"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Check access permissions
        if not check_camera_access(user, camera_id):
            return jsonify({'error': 'Access denied to this camera'}), 403
        
        def generate_mjpeg():
            """Generator function for MJPEG streaming"""
            try:
                while True:
                    async def _get_frame():
                        viam_service = get_viam_service()
                        return await viam_service.get_camera_image(camera_id, 'JPEG')
                    
                    # Run async function in event loop
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    frame = loop.run_until_complete(_get_frame())
                    loop.close()
                    
                    if frame:
                        yield (b'--frame\r\n'
                               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
                    else:
                        # Send placeholder frame if camera is not available
                        import time
                        time.sleep(1)
                        
            except Exception as e:
                print(f"Error in MJPEG stream: {e}")
                return
        
        # Create stream session
        session_id = f"{user_id}_{camera_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
        stream_session = StreamSession(
            user_id=user_id,
            camera_id=camera_id,
            session_id=session_id
        )
        db.session.add(stream_session)
        db.session.commit()
        
        return Response(
            generate_mjpeg(),
            mimetype='multipart/x-mixed-replace; boundary=frame',
            headers={
                'Cache-Control': 'no-cache, no-store, must-revalidate',
                'Pragma': 'no-cache',
                'Expires': '0',
                'X-Stream-Session': session_id
            }
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@viam_bp.route('/viam/stream/sessions', methods=['GET'])
@jwt_required()
@require_role(['super_admin', 'admin'])
def get_active_stream_sessions():
    """Get all active streaming sessions"""
    try:
        active_sessions = StreamSession.query.filter_by(is_active=True).all()
        
        sessions_data = []
        for session in active_sessions:
            user = User.query.get(session.user_id)
            sessions_data.append({
                'session_id': session.session_id,
                'user_id': session.user_id,
                'username': user.username if user else 'Unknown',
                'camera_id': session.camera_id,
                'started_at': session.started_at.isoformat(),
                'duration': session.get_duration()
            })
        
        return jsonify({
            'active_sessions': sessions_data,
            'total_sessions': len(sessions_data)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@viam_bp.route('/viam/stream/sessions/<session_id>/end', methods=['POST'])
@jwt_required()
def end_stream_session(session_id):
    """End a streaming session"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Find the session
        session = StreamSession.query.filter_by(session_id=session_id).first()
        
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        
        # Check if user owns the session or is admin
        if session.user_id != user_id and user.role not in ['super_admin', 'admin']:
            return jsonify({'error': 'Access denied to this session'}), 403
        
        # End the session
        session.end_session()
        db.session.commit()
        
        return jsonify({
            'message': 'Stream session ended successfully',
            'session_id': session_id,
            'duration': session.get_duration()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@viam_bp.route('/viam/cameras/<camera_id>/snapshot', methods=['POST'])
@jwt_required()
def take_camera_snapshot(camera_id):
    """Take a snapshot from camera and save it"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Check access permissions
        if not check_camera_access(user, camera_id):
            return jsonify({'error': 'Access denied to this camera'}), 403
        
        async def _take_snapshot():
            viam_service = get_viam_service()
            return await viam_service.get_camera_image(camera_id, 'JPEG')
        
        # Run async function in event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        image_data = loop.run_until_complete(_take_snapshot())
        loop.close()
        
        if not image_data:
            return jsonify({'error': 'Failed to capture snapshot'}), 500
        
        # Save snapshot to recordings directory
        import os
        recordings_dir = '/home/ubuntu/recordings/snapshots'
        os.makedirs(recordings_dir, exist_ok=True)
        
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = f"{camera_id}_snapshot_{timestamp}.jpg"
        filepath = os.path.join(recordings_dir, filename)
        
        with open(filepath, 'wb') as f:
            f.write(image_data)
        
        # TODO: Save snapshot record to database
        
        return jsonify({
            'message': 'Snapshot captured successfully',
            'camera_id': camera_id,
            'filename': filename,
            'filepath': filepath,
            'size_bytes': len(image_data),
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Health check for VIAM service
@viam_bp.route('/viam/health', methods=['GET'])
def viam_health_check():
    """Health check for VIAM service"""
    try:
        viam_service = get_viam_service()
        status = viam_service.get_connection_status()
        
        health_status = {
            'service': 'VIAM Integration',
            'status': 'healthy' if status['connected'] else 'unhealthy',
            'connection': status,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return jsonify(health_status), 200 if status['connected'] else 503
        
    except Exception as e:
        return jsonify({
            'service': 'VIAM Integration',
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

