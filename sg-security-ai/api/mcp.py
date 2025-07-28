from http.server import BaseHTTPRequestHandler
import json
import urllib.parse
from datetime import datetime, timedelta
import uuid

class handler(BaseHTTPRequestHandler):
    
    def _send_cors_headers(self):
        """Send CORS headers for MCP compatibility"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, DELETE')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With')
        
    def _send_json_response(self, data, status_code=200):
        """Send JSON response with proper headers"""
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self._send_cors_headers()
        self.end_headers()
        response_json = json.dumps(data, ensure_ascii=False, indent=2)
        self.wfile.write(response_json.encode('utf-8'))

    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self._send_cors_headers()
        self.end_headers()

    def do_GET(self):
        """Handle MCP GET requests - primarily for capabilities"""
        try:
            # MCP server capabilities response
            capabilities = {
                "protocol_version": "2024-11-05",
                "server_info": {
                    "name": "SG Security AI MCP Server",
                    "version": "1.0.0",
                    "description": "MCP server for SG Security AI surveillance system"
                },
                "capabilities": {
                    "tools": {
                        "list_changed": True
                    }
                },
                "tools": [
                    {
                        "name": "get_cameras_status",
                        "description": "Get the status of all security cameras in the system",
                        "inputSchema": {
                            "type": "object",
                            "properties": {}
                        }
                    },
                    {
                        "name": "get_security_events", 
                        "description": "Get recent security events from the surveillance system",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "limit": {
                                    "type": "integer",
                                    "minimum": 1,
                                    "maximum": 50,
                                    "default": 10,
                                    "description": "Number of events to retrieve"
                                },
                                "hours": {
                                    "type": "integer", 
                                    "minimum": 1,
                                    "maximum": 168,
                                    "default": 24,
                                    "description": "Time window in hours"
                                }
                            }
                        }
                    },
                    {
                        "name": "start_recording",
                        "description": "Start recording on a specific camera",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "camera_id": {
                                    "type": "string",
                                    "description": "ID of the camera to start recording"
                                },
                                "duration": {
                                    "type": "integer",
                                    "minimum": 30,
                                    "maximum": 3600,
                                    "default": 300,
                                    "description": "Recording duration in seconds"
                                }
                            },
                            "required": ["camera_id"]
                        }
                    },
                    {
                        "name": "capture_snapshot",
                        "description": "Capture a snapshot from a specific camera",
                        "inputSchema": {
                            "type": "object", 
                            "properties": {
                                "camera_id": {
                                    "type": "string",
                                    "description": "ID of the camera to capture snapshot from"
                                }
                            },
                            "required": ["camera_id"]
                        }
                    },
                    {
                        "name": "get_system_stats",
                        "description": "Get system statistics and health status",
                        "inputSchema": {
                            "type": "object",
                            "properties": {}
                        }
                    }
                ]
            }
            
            self._send_json_response(capabilities)
            
        except Exception as e:
            error_response = {
                "error": "Internal server error",
                "message": str(e)
            }
            self._send_json_response(error_response, 500)

    def do_POST(self):
        """Handle MCP POST requests - tool execution"""
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length > 0:
                post_data = self.rfile.read(content_length).decode('utf-8')
                request_data = json.loads(post_data)
            else:
                request_data = {}
            
            method = request_data.get('method', '')
            params = request_data.get('params', {})
            request_id = request_data.get('id', str(uuid.uuid4()))
            
            # Route to appropriate tool handler
            if method == 'tools/call':
                tool_name = params.get('name', '')
                tool_args = params.get('arguments', {})
                
                if tool_name == 'get_cameras_status':
                    result = self._get_cameras_status()
                elif tool_name == 'get_security_events':
                    result = self._get_security_events(tool_args)
                elif tool_name == 'start_recording':
                    result = self._start_recording(tool_args)
                elif tool_name == 'capture_snapshot':
                    result = self._capture_snapshot(tool_args)
                elif tool_name == 'get_system_stats':
                    result = self._get_system_stats()
                else:
                    result = {
                        "error": f"Unknown tool: {tool_name}",
                        "isError": True
                    }
                
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": result
                }
            else:
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
            
            self._send_json_response(response)
            
        except Exception as e:
            error_response = {
                "jsonrpc": "2.0", 
                "id": request_data.get('id', None) if 'request_data' in locals() else None,
                "error": {
                    "code": -32603,
                    "message": "Internal error",
                    "data": str(e)
                }
            }
            self._send_json_response(error_response, 500)

    def _get_cameras_status(self):
        """Get status of all cameras"""
        cameras = [
            {"id": "camera-1", "name": "Camera Principale", "status": "online", "location": "Ingresso"},
            {"id": "camera-2", "name": "Camera Secondaria", "status": "online", "location": "Giardino"}, 
            {"id": "video-store-camera-1", "name": "Camera Store 1", "status": "offline", "location": "Magazzino"},
            {"id": "video-store-camera-2", "name": "Camera Store 2", "status": "online", "location": "Ufficio"}
        ]
        
        status_text = "📹 Status Telecamere SG Security AI:\n\n"
        for cam in cameras:
            status_icon = "🟢 Online" if cam['status'] == 'online' else "🔴 Offline"
            status_text += f"• {cam['name']} ({cam['id']})\n  Status: {status_icon}\n  Posizione: {cam['location']}\n\n"
        
        return {
            "content": [{"type": "text", "text": status_text.strip()}],
            "isError": False
        }

    def _get_security_events(self, args):
        """Get recent security events"""
        limit = args.get('limit', 10)
        hours = args.get('hours', 24)
        
        # Generate sample events
        events = [
            {
                "id": "1",
                "type": "motion_detected", 
                "camera": "camera-1",
                "timestamp": (datetime.now() - timedelta(hours=2)).isoformat(),
                "severity": "medium",
                "description": "Movimento rilevato nell'area ingresso"
            },
            {
                "id": "2",
                "type": "person_detected",
                "camera": "camera-2", 
                "timestamp": (datetime.now() - timedelta(hours=4)).isoformat(),
                "severity": "high",
                "description": "Persona non autorizzata rilevata in giardino"
            },
            {
                "id": "3",
                "type": "camera_offline",
                "camera": "video-store-camera-1",
                "timestamp": (datetime.now() - timedelta(hours=6)).isoformat(),
                "severity": "high", 
                "description": "Camera magazzino disconnessa"
            }
        ][:limit]
        
        events_text = f"🚨 Eventi di Sicurezza (ultime {hours}h):\n\n"
        for event in events:
            severity_icon = "🔴" if event['severity'] == 'high' else "🟡" if event['severity'] == 'medium' else "🟢"
            type_icons = {"motion_detected": "👁️", "person_detected": "👤", "camera_offline": "📹"}
            type_icon = type_icons.get(event['type'], "📋")
            timestamp = datetime.fromisoformat(event['timestamp']).strftime('%d/%m/%Y %H:%M')
            
            events_text += f"{severity_icon} {type_icon} {event['description']}\n"
            events_text += f"  Camera: {event['camera']}\n"
            events_text += f"  Orario: {timestamp}\n"  
            events_text += f"  Gravità: {event['severity'].upper()}\n\n"
        
        return {
            "content": [{"type": "text", "text": events_text.strip()}],
            "isError": False
        }

    def _start_recording(self, args):
        """Start recording on specified camera"""
        camera_id = args.get('camera_id', '')
        duration = args.get('duration', 300)
        
        if not camera_id:
            return {
                "content": [{"type": "text", "text": "❌ Errore: camera_id richiesto"}],
                "isError": True
            }
        
        recording_text = f"📹 Registrazione avviata!\n\n"
        recording_text += f"• Camera: {camera_id}\n"
        recording_text += f"• Durata: {duration} secondi\n"
        recording_text += f"• Status: 🔴 Recording in corso\n"
        recording_text += f"• File: recording_{camera_id}_{int(datetime.now().timestamp())}.mp4"
        
        return {
            "content": [{"type": "text", "text": recording_text}],
            "isError": False
        }

    def _capture_snapshot(self, args):
        """Capture snapshot from specified camera"""
        camera_id = args.get('camera_id', '')
        
        if not camera_id:
            return {
                "content": [{"type": "text", "text": "❌ Errore: camera_id richiesto"}],
                "isError": True
            }
        
        snapshot_text = f"📸 Snapshot catturato!\n\n"
        snapshot_text += f"• Camera: {camera_id}\n"
        snapshot_text += f"• Timestamp: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n"
        snapshot_text += f"• File: snapshot_{camera_id}_{int(datetime.now().timestamp())}.jpg\n"
        snapshot_text += f"• Risoluzione: 1920x1080\n"
        snapshot_text += f"• Status: ✅ Salvato con successo"
        
        return {
            "content": [{"type": "text", "text": snapshot_text}],
            "isError": False
        }

    def _get_system_stats(self):
        """Get system statistics"""
        stats_text = "📊 Statistiche Sistema SG Security AI:\n\n"
        stats_text += "🔧 Status Sistema:\n"
        stats_text += "• Uptime: 72h 15m\n"
        stats_text += "• CPU: 15%\n"
        stats_text += "• Memoria: 42%\n\n"
        stats_text += "📹 Telecamere:\n"
        stats_text += "• Online: 3/4\n"
        stats_text += "• Registrazioni attive: 1\n\n"
        stats_text += "🗃️ Storage:\n"
        stats_text += "• Utilizzato: 2.4GB/50GB\n"
        stats_text += "• Disponibile: 95.2%\n\n"
        stats_text += "📈 Oggi:\n"
        stats_text += "• Eventi rilevati: 28"
        
        return {
            "content": [{"type": "text", "text": stats_text}],
            "isError": False
        }