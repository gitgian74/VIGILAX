from flask import Blueprint, jsonify, request, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
import os
from datetime import datetime

from src.models.user import User, Recording, db
from src.models.camera import Camera
from src.services.recording_service import get_recording_service

recording_bp = Blueprint('recording', __name__)

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

@recording_bp.route('/recordings', methods=['GET'])
@jwt_required()
def get_recordings():
    """Get recordings list with filtering and pagination"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 20, type=int), 100)
        camera_id = request.args.get('camera_id')
        recording_type = request.args.get('type')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        # Build query
        query = Recording.query
        
        # Filter by camera access for non-admin users
        if user.role not in ['super_admin', 'admin']:
            assigned_cameras = user.get_assigned_cameras()
            if assigned_cameras:
                query = query.filter(Recording.camera_id.in_(assigned_cameras))
            else:
                # User has no camera access
                return jsonify({
                    'recordings': [],
                    'total': 0,
                    'page': page,
                    'per_page': per_page,
                    'pages': 0
                })
        
        # Apply filters
        if camera_id:
            query = query.filter(Recording.camera_id == camera_id)
        
        if recording_type:
            query = query.filter(Recording.recording_type == recording_type)
        
        if start_date:
            try:
                start_dt = datetime.fromisoformat(start_date)
                query = query.filter(Recording.created_at >= start_dt)
            except ValueError:
                return jsonify({'error': 'Invalid start_date format'}), 400
        
        if end_date:
            try:
                end_dt = datetime.fromisoformat(end_date)
                query = query.filter(Recording.created_at <= end_dt)
            except ValueError:
                return jsonify({'error': 'Invalid end_date format'}), 400
        
        # Order by creation date (newest first)
        query = query.order_by(Recording.created_at.desc())
        
        # Paginate
        pagination = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        recordings_data = []
        for recording in pagination.items:
            # Get camera info
            camera = Camera.query.get(recording.camera_id)
            
            # Get user info
            recording_user = User.query.get(recording.user_id)
            
            recordings_data.append({
                'id': recording.id,
                'camera_id': recording.camera_id,
                'camera_name': camera.name if camera else 'Unknown',
                'user_id': recording.user_id,
                'username': recording_user.username if recording_user else 'Unknown',
                'filename': recording.filename,
                'file_path': recording.file_path,
                'duration': recording.duration,
                'file_size': recording.file_size,
                'recording_type': recording.recording_type,
                'created_at': recording.created_at.isoformat(),
                'ended_at': recording.ended_at.isoformat() if recording.ended_at else None,
                'metadata': recording.get_metadata(),
                'file_exists': os.path.exists(recording.file_path) if recording.file_path else False
            })
        
        return jsonify({
            'recordings': recordings_data,
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@recording_bp.route('/recordings/start', methods=['POST'])
@jwt_required()
def start_recording():
    """Start recording for a camera"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request data required'}), 400
        
        camera_id = data.get('camera_id')
        duration_minutes = data.get('duration_minutes')
        
        if not camera_id:
            return jsonify({'error': 'camera_id is required'}), 400
        
        # Check camera access
        if not check_camera_access(user, camera_id):
            return jsonify({'error': 'Access denied to this camera'}), 403
        
        # Validate duration
        if duration_minutes is not None:
            if not isinstance(duration_minutes, int) or duration_minutes <= 0:
                return jsonify({'error': 'duration_minutes must be a positive integer'}), 400
            if duration_minutes > 480:  # Max 8 hours
                return jsonify({'error': 'duration_minutes cannot exceed 480 (8 hours)'}), 400
        
        # Start recording
        recording_service = get_recording_service()
        result = recording_service.start_recording(camera_id, user_id, duration_minutes)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@recording_bp.route('/recordings/stop', methods=['POST'])
@jwt_required()
def stop_recording():
    """Stop recording for a camera"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request data required'}), 400
        
        camera_id = data.get('camera_id')
        
        if not camera_id:
            return jsonify({'error': 'camera_id is required'}), 400
        
        # Check camera access
        if not check_camera_access(user, camera_id):
            return jsonify({'error': 'Access denied to this camera'}), 403
        
        # Stop recording
        recording_service = get_recording_service()
        result = recording_service.stop_recording(camera_id)
        
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@recording_bp.route('/recordings/active', methods=['GET'])
@jwt_required()
def get_active_recordings():
    """Get list of active recordings"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        recording_service = get_recording_service()
        active_recordings = recording_service.get_active_recordings()
        
        # Filter by user access
        if user.role not in ['super_admin', 'admin']:
            assigned_cameras = user.get_assigned_cameras()
            active_recordings = [
                rec for rec in active_recordings 
                if rec['camera_id'] in assigned_cameras
            ]
        
        # Add camera names
        for recording in active_recordings:
            camera = Camera.query.get(recording['camera_id'])
            recording['camera_name'] = camera.name if camera else 'Unknown'
            
            # Add user info
            recording_user = User.query.get(recording['user_id'])
            recording['username'] = recording_user.username if recording_user else 'Unknown'
        
        return jsonify({
            'active_recordings': active_recordings,
            'total': len(active_recordings)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@recording_bp.route('/recordings/statistics', methods=['GET'])
@jwt_required()
@require_role(['super_admin', 'admin'])
def get_recording_statistics():
    """Get recording statistics (admin only)"""
    try:
        recording_service = get_recording_service()
        stats = recording_service.get_recording_statistics()
        
        return jsonify({'statistics': stats})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@recording_bp.route('/recordings/<int:recording_id>', methods=['GET'])
@jwt_required()
def get_recording_details(recording_id):
    """Get details of a specific recording"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        recording = Recording.query.get(recording_id)
        if not recording:
            return jsonify({'error': 'Recording not found'}), 404
        
        # Check access
        if user.role not in ['super_admin', 'admin']:
            if not check_camera_access(user, recording.camera_id):
                return jsonify({'error': 'Access denied to this recording'}), 403
        
        # Get camera info
        camera = Camera.query.get(recording.camera_id)
        
        # Get user info
        recording_user = User.query.get(recording.user_id)
        
        return jsonify({
            'recording': {
                'id': recording.id,
                'camera_id': recording.camera_id,
                'camera_name': camera.name if camera else 'Unknown',
                'user_id': recording.user_id,
                'username': recording_user.username if recording_user else 'Unknown',
                'filename': recording.filename,
                'file_path': recording.file_path,
                'duration': recording.duration,
                'file_size': recording.file_size,
                'recording_type': recording.recording_type,
                'created_at': recording.created_at.isoformat(),
                'ended_at': recording.ended_at.isoformat() if recording.ended_at else None,
                'metadata': recording.get_metadata(),
                'file_exists': os.path.exists(recording.file_path) if recording.file_path else False
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@recording_bp.route('/recordings/<int:recording_id>/download', methods=['GET'])
@jwt_required()
def download_recording(recording_id):
    """Download a recording file"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        recording = Recording.query.get(recording_id)
        if not recording:
            return jsonify({'error': 'Recording not found'}), 404
        
        # Check access
        if user.role not in ['super_admin', 'admin']:
            if not check_camera_access(user, recording.camera_id):
                return jsonify({'error': 'Access denied to this recording'}), 403
        
        # Check if file exists
        if not recording.file_path or not os.path.exists(recording.file_path):
            return jsonify({'error': 'Recording file not found'}), 404
        
        # Send file
        return send_file(
            recording.file_path,
            as_attachment=True,
            download_name=recording.filename or f"recording_{recording_id}.mp4",
            mimetype='video/mp4'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@recording_bp.route('/recordings/<int:recording_id>', methods=['DELETE'])
@jwt_required()
def delete_recording(recording_id):
    """Delete a recording"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        recording = Recording.query.get(recording_id)
        if not recording:
            return jsonify({'error': 'Recording not found'}), 404
        
        # Check permissions (only super admin or recording owner can delete)
        if user.role != 'super_admin' and recording.user_id != user_id:
            return jsonify({'error': 'Access denied'}), 403
        
        # Delete file if it exists
        if recording.file_path and os.path.exists(recording.file_path):
            try:
                os.remove(recording.file_path)
            except Exception as e:
                return jsonify({'error': f'Failed to delete file: {str(e)}'}), 500
        
        # Delete database record
        db.session.delete(recording)
        db.session.commit()
        
        return jsonify({'message': 'Recording deleted successfully'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@recording_bp.route('/recordings/cleanup', methods=['POST'])
@jwt_required()
@require_role(['super_admin'])
def cleanup_old_recordings():
    """Clean up old recordings based on retention policy"""
    try:
        recording_service = get_recording_service()
        result = recording_service.cleanup_old_recordings()
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Health check for recording service
@recording_bp.route('/recordings/health', methods=['GET'])
@jwt_required()
@require_role(['super_admin', 'admin'])
def recording_health_check():
    """Health check for recording service"""
    try:
        recording_service = get_recording_service()
        stats = recording_service.get_recording_statistics()
        
        # Check disk space
        disk_usage = stats.get('disk_usage', {})
        used_percentage = disk_usage.get('used_percentage', 0)
        
        health_status = {
            'service': 'Recording Service',
            'status': 'healthy' if used_percentage < 90 else 'warning',
            'active_recordings': stats.get('active_recordings', 0),
            'disk_usage_percentage': used_percentage,
            'total_recordings': stats.get('total_recordings', 0),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        if used_percentage >= 95:
            health_status['status'] = 'critical'
            health_status['warning'] = 'Disk space critically low'
        elif used_percentage >= 90:
            health_status['warning'] = 'Disk space running low'
        
        status_code = 200
        if health_status['status'] == 'warning':
            status_code = 503
        elif health_status['status'] == 'critical':
            status_code = 503
        
        return jsonify(health_status), status_code
        
    except Exception as e:
        return jsonify({
            'service': 'Recording Service',
            'status': 'error',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 500

