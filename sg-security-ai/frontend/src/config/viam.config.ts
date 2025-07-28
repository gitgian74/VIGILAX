import * as VIAM from '@viamrobotics/sdk';
import { CameraClient } from '@viamrobotics/sdk';

// Configurazione del robot Viam
export const ROBOT_CONFIG = {
  name: "ssa-locaratow-main",
  address: "ssa-locaratow-main.1j0se98dbn.viam.cloud",
  credentials: {
    type: "api-key" as const,
    payload: import.meta.env.VITE_VIAM_API_KEY || "4mkomaqzmpne49vnhh43dz3wsq33or3r",
    authEntity: import.meta.env.VITE_VIAM_API_KEY_ID || "50ad7296-b4f5-4c75-8262-90f2cedc2f74"
  },
  signalingAddress: "https://app.viam.com:443"
};

// Configurazione delle camere
export const CAMERAS_CONFIG = {
  camera1: {
    name: "camera-1",
    displayName: "Camera Esterna",
    recordingPath: "/home/gian/recordings/video"
  },
  camera2: {
    name: "camera-2", 
    displayName: "Camera Interna",
    recordingPath: "/home/gian/recordings/webcam"
  }
};

// Zone di sicurezza predefinite
export const SECURITY_ZONES = [
  {
    id: "zone-1",
    name: "Ingresso Principale",
    coordinates: { x1: 0, y1: 0, x2: 50, y2: 50 }, // Percentuali del frame
    type: "restricted" as const,
    activeHours: "always"
  },
  {
    id: "zone-2",
    name: "Area Parcheggio",
    coordinates: { x1: 50, y1: 0, x2: 100, y2: 50 },
    type: "monitored" as const,
    activeHours: "18:00-06:00" // Orario notturno
  }
];

// Tipi di eventi di sicurezza
export const SECURITY_EVENTS = {
  INTRUSION: "intrusion",
  MOTION_IN_RESTRICTED: "motion_in_restricted",
  UNAUTHORIZED_PRESENCE: "unauthorized_presence",
  LOITERING: "loitering",
  GATE_OPEN: "gate_open",
  GATE_CLOSE: "gate_close"
} as const;

// Configurazione del modello ML per detection
export const ML_CONFIG = {
  modelName: "ml_model_service",
  visionServiceName: "vision-1",
  confidenceThreshold: 0.7,
  loiteringThresholdSeconds: 30
};

// Singleton per la connessione robot
let robotClient: VIAM.RobotClient | null = null;

/**
 * Connette al robot Viam
 * @returns Promise con il client robot connesso
 */
export async function connectToRobot(): Promise<VIAM.RobotClient> {
  try {
    if (robotClient) {
      // Se già connesso, verifica che la connessione sia ancora valida
      try {
        await robotClient.resourceNames();
        return robotClient;
      } catch {
        // Se la connessione è caduta, riconnetti
        await robotClient.disconnect();
        robotClient = null;
      }
    }

    console.log('🤖 Connessione al robot Viam...');
    
    robotClient = await VIAM.createRobotClient({
      host: ROBOT_CONFIG.address,
      credential: {
        type: ROBOT_CONFIG.credentials.type,
        payload: ROBOT_CONFIG.credentials.payload
      },
      signalingAddress: ROBOT_CONFIG.signalingAddress
    });

    console.log('✅ Connesso al robot Viam');
    
    // Verifica risorse disponibili
    const resources = await robotClient.resourceNames();
    console.log('📋 Risorse disponibili:', resources);
    
    return robotClient;
  } catch (error) {
    console.error('❌ Errore connessione robot:', error);
    throw new Error(`Impossibile connettersi al robot: ${error}`);
  }
}

/**
 * Disconnette dal robot Viam
 */
export async function disconnectFromRobot(): Promise<void> {
  if (robotClient) {
    try {
      await robotClient.disconnect();
      robotClient = null;
      console.log('🔌 Disconnesso dal robot Viam');
    } catch (error) {
      console.error('Errore durante disconnessione:', error);
    }
  }
}

/**
 * Ottiene una camera specifica
 * @param cameraName Nome della camera
 * @returns Camera client
 */
export async function getCamera(cameraName: string): Promise<CameraClient> {
  const client = await connectToRobot();
  return new CameraClient(client, cameraName);
}

// Gestione eventi di sicurezza
export interface SecurityEvent {
  id: string;
  type: keyof typeof SECURITY_EVENTS;
  timestamp: Date;
  cameraName: string;
  zone?: string;
  confidence: number;
  details: {
    objectType?: string;
    duration?: number;
    position?: { x: number; y: number };
  };
  videoBufferPath?: string;
  processed: boolean;
  notificationsSent: boolean;
}

/**
 * Determina se un orario è autorizzato per una zona
 * @param zone Zona di sicurezza
 * @param time Orario da verificare
 * @returns true se autorizzato
 */
export function isAuthorizedTime(zone: typeof SECURITY_ZONES[0], time: Date = new Date()): boolean {
  if (zone.activeHours === "always") return true;
  
  const [startHour, endHour] = zone.activeHours.split("-").map(h => parseInt(h.split(":")[0]));
  const currentHour = time.getHours();
  
  // Gestisce orari che attraversano la mezzanotte
  if (startHour > endHour) {
    return currentHour >= startHour || currentHour < endHour;
  }
  
  return currentHour >= startHour && currentHour < endHour;
}

// Export types
export type RobotClient = VIAM.RobotClient;
export type StreamClient = VIAM.StreamClient;