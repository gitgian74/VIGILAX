from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

# Use the same db instance from user.py
from src.models.user import db

class Camera(db.Model):
    id = db.Column(db.String(50), primary_key=True)  # camera-1, camera-2, etc.
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(200))
    resolution = db.Column(db.String(20), default='1920x1080')
    fps = db.Column(db.Integer, default=30)
    recording_enabled = db.Column(db.Boolean, default=True)
    ai_analysis_enabled = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    viam_config = db.Column(db.Text)  # JSON configuration for VIAM
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime)

    def __repr__(self):
        return f'<Camera {self.id}>'

    def get_viam_config(self):
        """Get VIAM configuration as dictionary"""
        if self.viam_config:
            return json.loads(self.viam_config)
        return {}

    def set_viam_config(self, config_dict):
        """Set VIAM configuration from dictionary"""
        self.viam_config = json.dumps(config_dict)

    def update_last_seen(self):
        """Update last seen timestamp"""
        self.last_seen = datetime.utcnow()

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'location': self.location,
            'resolution': self.resolution,
            'fps': self.fps,
            'recording_enabled': self.recording_enabled,
            'ai_analysis_enabled': self.ai_analysis_enabled,
            'is_active': self.is_active,
            'viam_config': self.get_viam_config(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_seen': self.last_seen.isoformat() if self.last_seen else None
        }


class SystemConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text)
    description = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_by = db.Column(db.Integer)  # Remove foreign key for now

    def __repr__(self):
        return f'<SystemConfig {self.key}>'

    def get_value(self):
        """Get value as appropriate type"""
        try:
            return json.loads(self.value)
        except (json.JSONDecodeError, TypeError):
            return self.value

    def set_value(self, value):
        """Set value (converts to JSON if needed)"""
        if isinstance(value, (dict, list)):
            self.value = json.dumps(value)
        else:
            self.value = str(value)

    def to_dict(self):
        return {
            'id': self.id,
            'key': self.key,
            'value': self.get_value(),
            'description': self.description,
            'updated_at': self.updated_at.isoformat(),
            'updated_by': self.updated_by
        }


class StreamSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)  # Remove foreign key for now
    camera_id = db.Column(db.String(50), nullable=False)  # Remove foreign key for now
    session_id = db.Column(db.String(255), unique=True, nullable=False)
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    ended_at = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f'<StreamSession {self.session_id}>'

    def end_session(self):
        """End the streaming session"""
        self.ended_at = datetime.utcnow()
        self.is_active = False

    def get_duration(self):
        """Get session duration in seconds"""
        if self.ended_at:
            return int((self.ended_at - self.started_at).total_seconds())
        return int((datetime.utcnow() - self.started_at).total_seconds())

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'camera_id': self.camera_id,
            'session_id': self.session_id,
            'started_at': self.started_at.isoformat(),
            'ended_at': self.ended_at.isoformat() if self.ended_at else None,
            'is_active': self.is_active,
            'duration': self.get_duration()
        }

