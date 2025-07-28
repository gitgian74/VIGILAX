from flask import Blueprint, jsonify, request, Response
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from src.models.user import User
from src.models.camera import Camera, StreamSession, db
from datetime import datetime
import uuid
import json

camera_bp = Blueprint('camera', __name__)

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


@camera_bp.route('/cameras', methods=['GET'])
@jwt_required()
def get_cameras():
    """Get list of cameras accessible to user"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get cameras based on user role
        if user.role in ['super_admin', 'admin']:
            cameras = Camera.query.all()
        else:
            # Regular users only see assigned cameras
            assigned_camera_ids = user.get_assigned_cameras()
            cameras = Camera.query.filter(Camera.id.in_(assigned_camera_ids)).all()
        
        return jsonify({
            'cameras': [camera.to_dict() for camera in cameras],
            'total': len(cameras)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@camera_bp.route('/cameras', methods=['POST'])
@jwt_required()
@require_role(['super_admin', 'admin'])
def create_camera():
    """Create new camera (Admin+ only)"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['id', 'name']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Check if camera ID already exists
        existing_camera = Camera.query.get(data['id'])
        if existing_camera:
            return jsonify({'error': 'Camera ID already exists'}), 400
        
        # Create new camera
        camera = Camera(
            id=data['id'],
            name=data['name'],
            location=data.get('location', ''),
            resolution=data.get('resolution', '1920x1080'),
            fps=data.get('fps', 30),
            recording_enabled=data.get('recording_enabled', True),
            ai_analysis_enabled=data.get('ai_analysis_enabled', False)
        )
        
        # Set VIAM configuration if provided
        if 'viam_config' in data:
            camera.set_viam_config(data['viam_config'])
        
        db.session.add(camera)
        db.session.commit()
        
        return jsonify({
            'message': 'Camera created successfully',
            'camera': camera.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@camera_bp.route('/cameras/<camera_id>', methods=['GET'])
@jwt_required()
def get_camera(camera_id):
    """Get specific camera details"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        camera = Camera.query.get(camera_id)
        if not camera:
            return jsonify({'error': 'Camera not found'}), 404
        
        # Check access permissions
        if not check_camera_access(user, camera_id):
            return jsonify({'error': 'Access denied to this camera'}), 403
        
        return jsonify({'camera': camera.to_dict()})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@camera_bp.route('/cameras/<camera_id>', methods=['PUT'])
@jwt_required()
@require_role(['super_admin', 'admin'])
def update_camera(camera_id):
    """Update camera configuration (Admin+ only)"""
    try:
        camera = Camera.query.get(camera_id)
        if not camera:
            return jsonify({'error': 'Camera not found'}), 404
        
        data = request.get_json()
        
        # Update camera fields
        if 'name' in data:
            camera.name = data['name']
        
        if 'location' in data:
            camera.location = data['location']
        
        if 'resolution' in data:
            camera.resolution = data['resolution']
        
        if 'fps' in data:
            camera.fps = int(data['fps'])
        
        if 'recording_enabled' in data:
            camera.recording_enabled = bool(data['recording_enabled'])
        
        if 'ai_analysis_enabled' in data:
            camera.ai_analysis_enabled = bool(data['ai_analysis_enabled'])
        
        if 'is_active' in data:
            camera.is_active = bool(data['is_active'])
        
        if 'viam_config' in data:
            camera.set_viam_config(data['viam_config'])
        
        db.session.commit()
        
        return jsonify({
            'message': 'Camera updated successfully',
            'camera': camera.to_dict()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@camera_bp.route('/cameras/<camera_id>', methods=['DELETE'])
@jwt_required()
@require_role(['super_admin'])
def delete_camera(camera_id):
    """Delete camera (Super Admin only)"""
    try:
        camera = Camera.query.get(camera_id)
        if not camera:
            return jsonify({'error': 'Camera not found'}), 404
        
        # Delete related stream sessions
        StreamSession.query.filter_by(camera_id=camera_id).delete()
        
        # Delete camera
        db.session.delete(camera)
        db.session.commit()
        
        return jsonify({'message': 'Camera deleted successfully'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@camera_bp.route('/cameras/<camera_id>/stream', methods=['GET'])
@jwt_required()
def get_camera_stream(camera_id):
    """Get camera stream (placeholder for VIAM integration)"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        camera = Camera.query.get(camera_id)
        if not camera:
            return jsonify({'error': 'Camera not found'}), 404
        
        # Check access permissions
        if not check_camera_access(user, camera_id):
            return jsonify({'error': 'Access denied to this camera'}), 403
        
        if not camera.is_active:
            return jsonify({'error': 'Camera is not active'}), 400
        
        # Create stream session
        session_id = str(uuid.uuid4())
        stream_session = StreamSession(
            user_id=user_id,
            camera_id=camera_id,
            session_id=session_id
        )
        
        db.session.add(stream_session)
        db.session.commit()
        
        # Update camera last seen
        camera.update_last_seen()
        db.session.commit()
        
        # Return stream information (will be implemented with VIAM integration)
        return jsonify({
            'stream_url': f'/api/cameras/{camera_id}/stream/{session_id}',
            'session_id': session_id,
            'camera': camera.to_dict(),
            'message': 'Stream session created successfully'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@camera_bp.route('/cameras/<camera_id>/stream/<session_id>', methods=['DELETE'])
@jwt_required()
def end_camera_stream(camera_id, session_id):
    """End camera stream session"""
    try:
        user_id = get_jwt_identity()
        
        stream_session = StreamSession.query.filter_by(
            user_id=user_id,
            camera_id=camera_id,
            session_id=session_id,
            is_active=True
        ).first()
        
        if not stream_session:
            return jsonify({'error': 'Stream session not found'}), 404
        
        stream_session.end_session()
        db.session.commit()
        
        return jsonify({'message': 'Stream session ended successfully'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@camera_bp.route('/cameras/<camera_id>/snapshot', methods=['GET'])
@jwt_required()
def get_camera_snapshot(camera_id):
    """Get camera snapshot (placeholder for VIAM integration)"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        camera = Camera.query.get(camera_id)
        if not camera:
            return jsonify({'error': 'Camera not found'}), 404
        
        # Check access permissions
        if not check_camera_access(user, camera_id):
            return jsonify({'error': 'Access denied to this camera'}), 403
        
        if not camera.is_active:
            return jsonify({'error': 'Camera is not active'}), 400
        
        # Update camera last seen
        camera.update_last_seen()
        db.session.commit()
        
        # Placeholder response (will be implemented with VIAM integration)
        return jsonify({
            'snapshot_url': f'/api/cameras/{camera_id}/snapshot/{datetime.utcnow().isoformat()}',
            'camera': camera.to_dict(),
            'message': 'Snapshot request processed'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@camera_bp.route('/cameras/<camera_id>/status', methods=['GET'])
@jwt_required()
def get_camera_status(camera_id):
    """Get camera status and health"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        camera = Camera.query.get(camera_id)
        if not camera:
            return jsonify({'error': 'Camera not found'}), 404
        
        # Check access permissions
        if not check_camera_access(user, camera_id):
            return jsonify({'error': 'Access denied to this camera'}), 403
        
        # Get active stream sessions for this camera
        active_sessions = StreamSession.query.filter_by(
            camera_id=camera_id,
            is_active=True
        ).count()
        
        # Calculate uptime (placeholder)
        uptime_seconds = 0
        if camera.last_seen:
            uptime_seconds = int((datetime.utcnow() - camera.last_seen).total_seconds())
        
        status = {
            'camera_id': camera_id,
            'is_active': camera.is_active,
            'last_seen': camera.last_seen.isoformat() if camera.last_seen else None,
            'active_streams': active_sessions,
            'uptime_seconds': uptime_seconds,
            'recording_enabled': camera.recording_enabled,
            'ai_analysis_enabled': camera.ai_analysis_enabled,
            'resolution': camera.resolution,
            'fps': camera.fps
        }
        
        return jsonify({'status': status})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@camera_bp.route('/cameras/stats', methods=['GET'])
@jwt_required()
@require_role(['super_admin', 'admin'])
def get_camera_stats():
    """Get camera statistics (Admin+ only)"""
    try:
        stats = {
            'total_cameras': Camera.query.count(),
            'active_cameras': Camera.query.filter_by(is_active=True).count(),
            'inactive_cameras': Camera.query.filter_by(is_active=False).count(),
            'recording_enabled': Camera.query.filter_by(recording_enabled=True).count(),
            'ai_enabled': Camera.query.filter_by(ai_analysis_enabled=True).count(),
            'active_streams': StreamSession.query.filter_by(is_active=True).count()
        }
        
        return jsonify({'stats': stats})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

