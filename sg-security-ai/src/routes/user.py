from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from src.models.user import User, db

user_bp = Blueprint('user', __name__)

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


@user_bp.route('/users', methods=['GET'])
@jwt_required()
@require_role(['super_admin', 'admin'])
def get_users():
    """Get list of users (Admin+ only)"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
        
        # Super admin can see all users, admin can see non-super-admin users
        if current_user.role == 'super_admin':
            users = User.query.all()
        else:  # admin
            users = User.query.filter(User.role != 'super_admin').all()
        
        return jsonify({
            'users': [user.to_dict() for user in users],
            'total': len(users)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@user_bp.route('/users', methods=['POST'])
@jwt_required()
@require_role(['super_admin', 'admin'])
def create_user():
    """Create new user (Admin+ only)"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['username', 'email', 'password', 'role']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} is required'}), 400
        
        # Validate role permissions
        new_user_role = data['role']
        if new_user_role not in ['super_admin', 'admin', 'user']:
            return jsonify({'error': 'Invalid role'}), 400
        
        # Only super admin can create super admin users
        if new_user_role == 'super_admin' and current_user.role != 'super_admin':
            return jsonify({'error': 'Only super admin can create super admin users'}), 403
        
        # Admin can only create admin and user roles
        if current_user.role == 'admin' and new_user_role == 'super_admin':
            return jsonify({'error': 'Admins cannot create super admin users'}), 403
        
        # Check if username or email already exists
        existing_user = User.query.filter(
            (User.username == data['username']) | (User.email == data['email'])
        ).first()
        
        if existing_user:
            return jsonify({'error': 'Username or email already exists'}), 400
        
        # Validate password
        if len(data['password']) < 6:
            return jsonify({'error': 'Password must be at least 6 characters'}), 400
        
        # Create new user
        user = User(
            username=data['username'],
            email=data['email'],
            role=new_user_role
        )
        user.set_password(data['password'])
        
        # Set assigned cameras if provided
        if 'assigned_cameras' in data:
            user.set_assigned_cameras(data['assigned_cameras'])
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'message': 'User created successfully',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@user_bp.route('/users/<int:user_id>', methods=['GET'])
@jwt_required()
@require_role(['super_admin', 'admin'])
def get_user(user_id):
    """Get specific user details (Admin+ only)"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return jsonify({'error': 'Current user not found'}), 404
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Admin cannot view super admin users
        if current_user.role == 'admin' and user.role == 'super_admin':
            return jsonify({'error': 'Access denied'}), 403
        
        return jsonify({'user': user.to_dict()})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@user_bp.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required()
@require_role(['super_admin', 'admin'])
def update_user(user_id):
    """Update user (Admin+ only)"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return jsonify({'error': 'Current user not found'}), 404
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Admin cannot modify super admin users
        if current_user.role == 'admin' and user.role == 'super_admin':
            return jsonify({'error': 'Access denied'}), 403
        
        # Users cannot modify themselves through this endpoint
        if user_id == current_user_id:
            return jsonify({'error': 'Use profile endpoint to modify your own account'}), 400
        
        data = request.get_json()
        
        # Update username if provided
        if 'username' in data:
            existing_user = User.query.filter(
                User.username == data['username'],
                User.id != user_id
            ).first()
            if existing_user:
                return jsonify({'error': 'Username already exists'}), 400
            user.username = data['username']
        
        # Update email if provided
        if 'email' in data:
            existing_user = User.query.filter(
                User.email == data['email'],
                User.id != user_id
            ).first()
            if existing_user:
                return jsonify({'error': 'Email already exists'}), 400
            user.email = data['email']
        
        # Update password if provided
        if 'password' in data and data['password']:
            if len(data['password']) < 6:
                return jsonify({'error': 'Password must be at least 6 characters'}), 400
            user.set_password(data['password'])
        
        # Update role if provided
        if 'role' in data:
            new_role = data['role']
            if new_role not in ['super_admin', 'admin', 'user']:
                return jsonify({'error': 'Invalid role'}), 400
            
            # Only super admin can set super admin role
            if new_role == 'super_admin' and current_user.role != 'super_admin':
                return jsonify({'error': 'Only super admin can assign super admin role'}), 403
            
            user.role = new_role
        
        # Update active status if provided
        if 'is_active' in data:
            user.is_active = bool(data['is_active'])
        
        # Update assigned cameras if provided
        if 'assigned_cameras' in data:
            user.set_assigned_cameras(data['assigned_cameras'])
        
        db.session.commit()
        
        return jsonify({
            'message': 'User updated successfully',
            'user': user.to_dict()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
@require_role(['super_admin'])
def delete_user(user_id):
    """Delete user (Super Admin only)"""
    try:
        current_user_id = get_jwt_identity()
        
        # Cannot delete yourself
        if user_id == current_user_id:
            return jsonify({'error': 'Cannot delete your own account'}), 400
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Delete user sessions first
        from src.models.user import UserSession
        UserSession.query.filter_by(user_id=user_id).delete()
        
        # Delete user
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({'message': 'User deleted successfully'})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@user_bp.route('/users/<int:user_id>/toggle-status', methods=['POST'])
@jwt_required()
@require_role(['super_admin', 'admin'])
def toggle_user_status(user_id):
    """Toggle user active status (Admin+ only)"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return jsonify({'error': 'Current user not found'}), 404
        
        # Cannot toggle yourself
        if user_id == current_user_id:
            return jsonify({'error': 'Cannot toggle your own status'}), 400
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Admin cannot toggle super admin users
        if current_user.role == 'admin' and user.role == 'super_admin':
            return jsonify({'error': 'Access denied'}), 403
        
        user.is_active = not user.is_active
        
        # If deactivating user, remove their sessions
        if not user.is_active:
            from src.models.user import UserSession
            UserSession.query.filter_by(user_id=user_id).delete()
        
        db.session.commit()
        
        status = 'activated' if user.is_active else 'deactivated'
        return jsonify({
            'message': f'User {status} successfully',
            'user': user.to_dict()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@user_bp.route('/users/stats', methods=['GET'])
@jwt_required()
@require_role(['super_admin', 'admin'])
def get_user_stats():
    """Get user statistics (Admin+ only)"""
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get user counts by role
        if current_user.role == 'super_admin':
            stats = {
                'total_users': User.query.count(),
                'super_admins': User.query.filter_by(role='super_admin').count(),
                'admins': User.query.filter_by(role='admin').count(),
                'users': User.query.filter_by(role='user').count(),
                'active_users': User.query.filter_by(is_active=True).count(),
                'inactive_users': User.query.filter_by(is_active=False).count()
            }
        else:  # admin
            stats = {
                'total_users': User.query.filter(User.role != 'super_admin').count(),
                'admins': User.query.filter_by(role='admin').count(),
                'users': User.query.filter_by(role='user').count(),
                'active_users': User.query.filter(
                    User.is_active == True,
                    User.role != 'super_admin'
                ).count(),
                'inactive_users': User.query.filter(
                    User.is_active == False,
                    User.role != 'super_admin'
                ).count()
            }
        
        return jsonify({'stats': stats})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

