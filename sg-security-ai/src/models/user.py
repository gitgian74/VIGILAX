from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import bcrypt
import json

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum('super_admin', 'admin', 'user', name='user_roles'), nullable=False, default='user')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    assigned_cameras = db.Column(db.Text)  # JSON array of camera IDs

    def __repr__(self):
        return f'<User {self.username}>'

    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        """Check if provided password matches hash"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

    def get_assigned_cameras(self):
        """Get list of assigned camera IDs"""
        if self.assigned_cameras:
            return json.loads(self.assigned_cameras)
        return []

    def set_assigned_cameras(self, camera_ids):
        """Set assigned camera IDs"""
        self.assigned_cameras = json.dumps(camera_ids)

    def has_camera_access(self, camera_id):
        """Check if user has access to specific camera"""
        if self.role in ['super_admin', 'admin']:
            return True
        return camera_id in self.get_assigned_cameras()

    def can_manage_users(self):
        """Check if user can manage other users"""
        return self.role in ['super_admin', 'admin']

    def can_delete_users(self):
        """Check if user can delete other users"""
        return self.role == 'super_admin'

    def can_access_all_recordings(self):
        """Check if user can access all recordings"""
        return self.role in ['super_admin', 'admin']

    def to_dict(self, include_sensitive=False):
        """Convert user to dictionary"""
        data = {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'is_active': self.is_active,
            'assigned_cameras': self.get_assigned_cameras()
        }
        
        if include_sensitive:
            data['password_hash'] = self.password_hash
            
        return data


class UserSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    session_token = db.Column(db.String(255), unique=True, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref=db.backref('sessions', lazy=True))

    def __repr__(self):
        return f'<UserSession {self.session_token[:10]}...>'

    def is_expired(self):
        """Check if session is expired"""
        return datetime.utcnow() > self.expires_at

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'session_token': self.session_token,
            'expires_at': self.expires_at.isoformat(),
            'created_at': self.created_at.isoformat()
        }


class Recording(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    camera_id = db.Column(db.String(50), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    file_size = db.Column(db.BigInteger, nullable=False)
    duration = db.Column(db.Integer, nullable=False)  # in seconds
    resolution = db.Column(db.String(20))
    fps = db.Column(db.Integer)
    has_ai_analysis = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Recording {self.filename}>'

    def to_dict(self):
        return {
            'id': self.id,
            'camera_id': self.camera_id,
            'filename': self.filename,
            'file_path': self.file_path,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat(),
            'file_size': self.file_size,
            'duration': self.duration,
            'resolution': self.resolution,
            'fps': self.fps,
            'has_ai_analysis': self.has_ai_analysis,
            'created_at': self.created_at.isoformat()
        }


class AIEvent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    recording_id = db.Column(db.Integer, db.ForeignKey('recording.id'), nullable=False)
    event_type = db.Column(db.String(50), nullable=False)
    confidence = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    bounding_box = db.Column(db.Text)  # JSON format
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    recording = db.relationship('Recording', backref=db.backref('ai_events', lazy=True))

    def __repr__(self):
        return f'<AIEvent {self.event_type}>'

    def get_bounding_box(self):
        """Get bounding box as dictionary"""
        if self.bounding_box:
            return json.loads(self.bounding_box)
        return None

    def set_bounding_box(self, bbox_dict):
        """Set bounding box from dictionary"""
        self.bounding_box = json.dumps(bbox_dict)

    def to_dict(self):
        return {
            'id': self.id,
            'recording_id': self.recording_id,
            'event_type': self.event_type,
            'confidence': self.confidence,
            'timestamp': self.timestamp.isoformat(),
            'bounding_box': self.get_bounding_box(),
            'description': self.description,
            'created_at': self.created_at.isoformat()
        }

