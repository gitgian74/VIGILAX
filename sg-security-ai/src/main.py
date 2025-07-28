import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, jsonify
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from datetime import timedelta

# Import models first
from src.models.user import db, User, UserSession, Recording, AIEvent
from src.models.camera import Camera, SystemConfig, StreamSession

# Import routes
from src.routes.user import user_bp
from src.routes.auth import auth_bp
from src.routes.camera import camera_bp
from src.routes.viam_routes import viam_bp
from src.routes.recording_routes import recording_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'sg-security-ai-secret-key-2025')
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'sg-security-jwt-key-2025')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)

# Database configuration
database_path = os.path.join(os.path.dirname(__file__), 'database', 'app.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{database_path}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
jwt = JWTManager(app)
CORS(app, origins="*")  # Allow all origins for development

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/api')
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(camera_bp, url_prefix='/api')
app.register_blueprint(viam_bp, url_prefix='/api')
app.register_blueprint(recording_bp, url_prefix='/api')

# JWT error handlers
@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    return jsonify({'error': 'Token has expired'}), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    return jsonify({'error': 'Invalid token'}), 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    return jsonify({'error': 'Authorization token is required'}), 401

# Initialize database and create default data
def init_database():
    """Initialize database with default data"""
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Create default super admin user if not exists
        super_admin = User.query.filter_by(role='super_admin').first()
        if not super_admin:
            admin_user = User(
                username='admin',
                email='admin@sg-security.local',
                role='super_admin'
            )
            admin_user.set_password('admin123')  # Change this in production!
            db.session.add(admin_user)
            
            print("Created default super admin user:")
            print("Username: admin")
            print("Password: admin123")
            print("Please change the password after first login!")
        
        # Create default cameras if not exist
        cameras_config = [
            {
                'id': 'camera-1',
                'name': 'Camera Principale',
                'location': 'Ingresso',
                'resolution': '1920x1080',
                'fps': 30,
                'recording_enabled': True,
                'ai_analysis_enabled': True
            },
            {
                'id': 'camera-2',
                'name': 'Camera Secondaria',
                'location': 'Corridoio',
                'resolution': '1280x720',
                'fps': 25,
                'recording_enabled': True,
                'ai_analysis_enabled': False
            }
        ]
        
        for camera_config in cameras_config:
            existing_camera = Camera.query.get(camera_config['id'])
            if not existing_camera:
                camera = Camera(**camera_config)
                db.session.add(camera)
        
        # Create default system configuration
        default_configs = [
            {
                'key': 'recording_path',
                'value': '/home/ubuntu/recordings/',
                'description': 'Base path for video recordings'
            },
            {
                'key': 'max_recording_size_gb',
                'value': '100',
                'description': 'Maximum storage size for recordings in GB'
            },
            {
                'key': 'retention_days',
                'value': '30',
                'description': 'Number of days to keep recordings'
            },
            {
                'key': 'ai_confidence_threshold',
                'value': '0.8',
                'description': 'Minimum confidence threshold for AI detections'
            }
        ]
        
        for config in default_configs:
            existing_config = SystemConfig.query.filter_by(key=config['key']).first()
            if not existing_config:
                system_config = SystemConfig(**config)
                db.session.add(system_config)
        
        db.session.commit()

# API info endpoint
@app.route('/api/info', methods=['GET'])
def api_info():
    """Get API information"""
    return jsonify({
        'name': 'SG Security AI System',
        'version': '1.0.0',
        'description': 'AI-powered video surveillance system with VIAM integration',
        'endpoints': {
            'auth': '/api/auth/*',
            'users': '/api/users/*',
            'cameras': '/api/cameras/*'
        }
    })

# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Check database connection
        db.session.execute('SELECT 1')
        
        # Get basic stats
        user_count = User.query.count()
        camera_count = Camera.query.count()
        active_streams = StreamSession.query.filter_by(is_active=True).count()
        
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'stats': {
                'users': user_count,
                'cameras': camera_count,
                'active_streams': active_streams
            }
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

# Serve frontend files
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "Frontend not found. Please build the frontend first.", 404

if __name__ == '__main__':
    # Initialize database
    init_database()
    
    # Start the application
    print("Starting SG Security AI System...")
    print("Access the application at: http://localhost:8080")
    print("API documentation available at: http://localhost:8080/api/info")
    
    app.run(host='0.0.0.0', port=8080, debug=True)

