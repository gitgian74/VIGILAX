import { z } from 'zod';
import { createMcpHandler } from 'mcp-handler';

const handler = createMcpHandler(
  (server) => {
    // Tool per ottenere status delle telecamere
    server.tool(
      'get_cameras_status',
      'Get the status of all security cameras in the system',
      {},
      async () => {
        try {
          // Simula chiamata alle API Appwrite per ottenere status telecamere
          const cameras = [
            { id: 'camera-1', name: 'Camera Principale', status: 'online', location: 'Ingresso' },
            { id: 'camera-2', name: 'Camera Secondaria', status: 'online', location: 'Giardino' },
            { id: 'video-store-camera-1', name: 'Camera Store 1', status: 'offline', location: 'Magazzino' },
            { id: 'video-store-camera-2', name: 'Camera Store 2', status: 'online', location: 'Ufficio' }
          ];
          
          return {
            content: [{
              type: 'text',
              text: `📹 Status Telecamere SG Security AI:\n\n${cameras.map(cam => 
                `• ${cam.name} (${cam.id})\n  Status: ${cam.status === 'online' ? '🟢 Online' : '🔴 Offline'}\n  Posizione: ${cam.location}`
              ).join('\n\n')}`
            }]
          };
        } catch (error) {
          return {
            content: [{
              type: 'text',
              text: `❌ Errore nel recupero status telecamere: ${error}`
            }]
          };
        }
      }
    );

    // Tool per ottenere eventi di sicurezza recenti
    server.tool(
      'get_security_events',
      'Get recent security events from the surveillance system',
      { 
        limit: z.number().int().min(1).max(50).optional().default(10),
        hours: z.number().int().min(1).max(168).optional().default(24)
      },
      async ({ limit, hours }) => {
        try {
          // Simula eventi di sicurezza
          const events = [
            {
              id: '1',
              type: 'motion_detected',
              camera: 'camera-1',
              timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
              severity: 'medium',
              description: 'Movimento rilevato nell\'area ingresso'
            },
            {
              id: '2', 
              type: 'person_detected',
              camera: 'camera-2',
              timestamp: new Date(Date.now() - 4 * 60 * 60 * 1000).toISOString(),
              severity: 'high',
              description: 'Persona non autorizzata rilevata in giardino'
            },
            {
              id: '3',
              type: 'camera_offline',
              camera: 'video-store-camera-1',
              timestamp: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString(),
              severity: 'high',
              description: 'Camera magazzino disconnessa'
            }
          ].slice(0, limit);

          return {
            content: [{
              type: 'text',
              text: `🚨 Eventi di Sicurezza (ultime ${hours}h):\n\n${events.map(event => {
                const severityIcon = event.severity === 'high' ? '🔴' : event.severity === 'medium' ? '🟡' : '🟢';
                const typeIcon = event.type === 'motion_detected' ? '👁️' : event.type === 'person_detected' ? '👤' : '📹';
                return `${severityIcon} ${typeIcon} ${event.description}\n  Camera: ${event.camera}\n  Orario: ${new Date(event.timestamp).toLocaleString('it-IT')}\n  Gravità: ${event.severity.toUpperCase()}`;
              }).join('\n\n')}`
            }]
          };
        } catch (error) {
          return {
            content: [{
              type: 'text',
              text: `❌ Errore nel recupero eventi: ${error}`
            }]
          };
        }
      }
    );

    // Tool per avviare registrazione
    server.tool(
      'start_recording',
      'Start recording on a specific camera',
      {
        camera_id: z.string().describe('ID of the camera to start recording'),
        duration: z.number().int().min(30).max(3600).optional().default(300).describe('Recording duration in seconds')
      },
      async ({ camera_id, duration }) => {
        try {
          return {
            content: [{
              type: 'text',
              text: `📹 Registrazione avviata!\n\n• Camera: ${camera_id}\n• Durata: ${duration} secondi\n• Status: 🔴 Recording in corso\n• File: recording_${camera_id}_${Date.now()}.mp4`
            }]
          };
        } catch (error) {
          return {
            content: [{
              type: 'text', 
              text: `❌ Errore nell'avvio registrazione: ${error}`
            }]
          };
        }
      }
    );

    // Tool per ottenere snapshot da telecamera
    server.tool(
      'capture_snapshot',
      'Capture a snapshot from a specific camera',
      {
        camera_id: z.string().describe('ID of the camera to capture snapshot from')
      },
      async ({ camera_id }) => {
        try {
          return {
            content: [{
              type: 'text',
              text: `📸 Snapshot catturato!\n\n• Camera: ${camera_id}\n• Timestamp: ${new Date().toLocaleString('it-IT')}\n• File: snapshot_${camera_id}_${Date.now()}.jpg\n• Risoluzione: 1920x1080\n• Status: ✅ Salvato con successo`
            }]
          };
        } catch (error) {
          return {
            content: [{
              type: 'text',
              text: `❌ Errore nella cattura snapshot: ${error}`
            }]
          };
        }
      }
    );

    // Tool per ottenere statistiche sistema
    server.tool(
      'get_system_stats',
      'Get system statistics and health status',
      {},
      async () => {
        try {
          const stats = {
            uptime: '72h 15m',
            cameras_online: 3,
            cameras_total: 4,
            events_today: 28,
            recordings_active: 1,
            storage_used: '2.4GB',
            storage_total: '50GB',
            cpu_usage: '15%',
            memory_usage: '42%'
          };

          return {
            content: [{
              type: 'text',
              text: `📊 Statistiche Sistema SG Security AI:\n\n🔧 Status Sistema:\n• Uptime: ${stats.uptime}\n• CPU: ${stats.cpu_usage}\n• Memoria: ${stats.memory_usage}\n\n📹 Telecamere:\n• Online: ${stats.cameras_online}/${stats.cameras_total}\n• Registrazioni attive: ${stats.recordings_active}\n\n🗃️ Storage:\n• Utilizzato: ${stats.storage_used}/${stats.storage_total}\n• Disponibile: ${((50 - 2.4) / 50 * 100).toFixed(1)}%\n\n📈 Oggi:\n• Eventi rilevati: ${stats.events_today}`
            }]
          };
        } catch (error) {
          return {
            content: [{
              type: 'text',
              text: `❌ Errore nel recupero statistiche: ${error}`
            }]
          };
        }
      }
    );
  },
  {},
  { basePath: '/api' }
);

export { handler as GET, handler as POST, handler as DELETE };