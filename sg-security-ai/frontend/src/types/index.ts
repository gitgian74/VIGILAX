// User and Authentication Types
export type UserRole = 'super_admin' | 'admin' | 'user';

export interface User {
  id: string;
  email: string;
  name: string;
  role: UserRole;
  avatar?: string;
  phone?: string;
  notificationPreferences: NotificationPreferences;
  createdAt: Date;
  updatedAt: Date;
}

export interface NotificationPreferences {
  email: boolean;
  sms: boolean;
  securityAlerts: boolean;
  dailyReports: boolean;
}

export interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

// Security Event Types
export type SecurityEventType = 
  | 'intrusion'
  | 'motion_in_restricted'
  | 'unauthorized_presence'
  | 'loitering'
  | 'gate_open'
  | 'gate_close';

export type EventSeverity = 'low' | 'medium' | 'high' | 'critical';

export interface SecurityEvent {
  id: string;
  type: SecurityEventType;
  timestamp: Date;
  cameraName: string;
  cameraDisplayName: string;
  zone?: SecurityZone;
  confidence: number;
  severity: EventSeverity;
  details: EventDetails;
  videoBufferUrl?: string;
  snapshotUrl?: string;
  processed: boolean;
  notificationsSent: boolean;
  acknowledgedBy?: string;
  acknowledgedAt?: Date;
}

export interface EventDetails {
  objectType?: string;
  objectCount?: number;
  duration?: number;
  position?: Position;
  direction?: 'entering' | 'exiting' | 'stationary';
  speed?: number;
}

export interface Position {
  x: number;
  y: number;
  width?: number;
  height?: number;
}

// Security Zone Types
export type ZoneType = 'restricted' | 'monitored' | 'safe';

export interface SecurityZone {
  id: string;
  name: string;
  description?: string;
  type: ZoneType;
  coordinates: ZoneCoordinates;
  cameras: string[];
  activeHours: string;
  enabled: boolean;
  rules: SecurityRule[];
  createdBy: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface ZoneCoordinates {
  x1: number;
  y1: number;
  x2: number;
  y2: number;
}

// Camera and Streaming Types
export interface Camera {
  name: string;
  displayName: string;
  status: CameraStatus;
  stream?: MediaStream;
  lastFrame?: string;
  recordingPath: string;
  capabilities: CameraCapabilities;
}

export type CameraStatus = 'online' | 'offline' | 'connecting' | 'error';

export interface CameraCapabilities {
  resolution: { width: number; height: number };
  frameRate: number;
  hasNightVision: boolean;
  hasPTZ: boolean;
  hasAudio: boolean;
}

// Security Rule Types
export interface SecurityRule {
  id: string;
  name: string;
  description?: string;
  type: 'time_based' | 'zone_based' | 'object_based';
  conditions: Record<string, unknown>;
  actions: {
    notify: boolean;
    record: boolean;
    alert: boolean;
  };
  severity: EventSeverity;
  enabled: boolean;
  createdBy: string;
  createdAt: Date;
  updatedAt: Date;
}
