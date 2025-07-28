from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from datetime import datetime, timedelta
from src.models.user import User, UserSession, db
import uuid

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/auth/login', methods=['POST'])
def login():
    """User login endpoint"""
    try:
        data = request.get_json()
        
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({'error': 'Username and password required'}), 400
        
        username = data['username']
        password = data['password']
        
        # Find user by username or email
        user = User.query.filter(
            (User.username == username) | (User.email == username)
        ).first()
        
        if not user or not user.check_password(password):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        if not user.is_active:
            return jsonify({'error': 'Account is disabled'}), 401
        
        # Update last login
        user.last_login = datetime.utcnow()
        
        # Create JWT token
        additional_claims = {
            'role': user.role,
            'user_id': user.id
        }
        access_token = create_access_token(
            identity=user.id,
            additional_claims=additional_claims,
            expires_delta=timedelta(hours=24)
        )
        
        # Create session record
        session_token = str(uuid.uuid4())
        session = UserSession(
            user_id=user.id,
            session_token=session_token,
            expires_at=datetime.utcnow() + timedelta(hours=24)
        )
        
        db.session.add(session)
        db.session.commit()
        
        return jsonify({
            'access_token': access_token,
            'session_token': session_token,
            'user': user.to_dict(),
            'expires_in': 24 * 3600  # 24 hours in seconds
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/auth/logout', methods=['POST'])
@jwt_required()
def logout():
    """User logout endpoint"""
    try:
        user_id = get_jwt_identity()
        
        # Get session token from request
        data = request.get_json() or {}
        session_token = data.get('session_token')
        
        if session_token:
            # Invalidate specific session
            session = UserSession.query.filter_by(
                user_id=user_id,
                session_token=session_token
            ).first()
            
            if session:
                db.session.delete(session)
        else:
            # Invalidate all user sessions
            UserSession.query.filter_by(user_id=user_id).delete()
        
        db.session.commit()
        
        return jsonify({'message': 'Logged out successfully'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/auth/refresh', methods=['POST'])
@jwt_required()
def refresh():
    """Refresh JWT token"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or not user.is_active:
            return jsonify({'error': 'Invalid user'}), 401
        
        # Create new JWT token
        additional_claims = {
            'role': user.role,
            'user_id': user.id
        }
        access_token = create_access_token(
            identity=user.id,
            additional_claims=additional_claims,
            expires_delta=timedelta(hours=24)
        )
        
        return jsonify({
            'access_token': access_token,
            'expires_in': 24 * 3600
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/auth/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get current user profile"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({'user': user.to_dict()})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/auth/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update current user profile"""
    try:
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        # Update allowed fields
        if 'email' in data:
            # Check if email is already taken
            existing_user = User.query.filter(
                User.email == data['email'],
                User.id != user_id
            ).first()
            if existing_user:
                return jsonify({'error': 'Email already in use'}), 400
            user.email = data['email']
        
        if 'password' in data and data['password']:
            if len(data['password']) < 6:
                return jsonify({'error': 'Password must be at least 6 characters'}), 400
            user.set_password(data['password'])
        
        db.session.commit()
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': user.to_dict()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/auth/sessions', methods=['GET'])
@jwt_required()
def get_sessions():
    """Get user's active sessions"""
    try:
        user_id = get_jwt_identity()
        
        sessions = UserSession.query.filter_by(user_id=user_id).all()
        
        # Clean up expired sessions
        current_time = datetime.utcnow()
        expired_sessions = [s for s in sessions if s.expires_at < current_time]
        
        for session in expired_sessions:
            db.session.delete(session)
        
        db.session.commit()
        
        # Get active sessions
        active_sessions = [s for s in sessions if s.expires_at >= current_time]
        
        return jsonify({
            'sessions': [session.to_dict() for session in active_sessions]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@auth_bp.route('/auth/sessions/<session_token>', methods=['DELETE'])
@jwt_required()
def delete_session(session_token):
    """Delete specific session"""
    try:
        user_id = get_jwt_identity()
        
        session = UserSession.query.filter_by(
            user_id=user_id,
            session_token=session_token
        ).first()
        
        if not session:
            return jsonify({'error': 'Session not found'}), 404
        
        db.session.delete(session)
        db.session.commit()
        
        return jsonify({'message': 'Session deleted successfully'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

