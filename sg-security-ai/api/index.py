from http.server import BaseHTTPRequestHandler
import json
import urllib.parse

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path
        
        # API endpoints
        if path == '/api/info':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {
                'name': 'SG Security AI',
                'version': '1.0.0',
                'status': 'running',
                'platform': 'Local'
            }
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        elif path == '/api/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {'status': 'healthy'}
            self.wfile.write(json.dumps(response).encode('utf-8'))
            
        else:
            # For all other routes, return 404 as the frontend should handle routing
            self.send_error(404)

    def do_POST(self):
        path = urllib.parse.urlparse(self.path).path
        
        if path == '/api/auth/login':
            try:
                content_length = int(self.headers['Content-Length'])
                data = json.loads(self.rfile.read(content_length).decode('utf-8'))
                
                # Demo authentication
                success = data.get('username') == 'admin' and data.get('password') == 'admin123'
                response = {
                    'success': success,
                    'token': 'demo-token-12345' if success else None,
                    'user': {'username': 'admin', 'role': 'admin'} if success else None,
                    'message': 'Login successful' if success else 'Invalid credentials'
                }
                
                self.send_response(200 if success else 401)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(response).encode('utf-8'))
                
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                error_response = {'error': 'Internal server error', 'message': str(e)}
                self.wfile.write(json.dumps(error_response).encode('utf-8'))
        else:
            self.send_error(404)
    
    def do_OPTIONS(self):
        # Handle CORS preflight requests
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        self.end_headers()