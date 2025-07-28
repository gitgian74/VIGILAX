import { Client, Account, Databases, Storage, Functions, Teams } from 'appwrite';

export const appwriteConfig = {
  endpoint: import.meta.env.VITE_APPWRITE_ENDPOINT || 'https://fra.cloud.appwrite.io/v1',
  projectId: import.meta.env.VITE_APPWRITE_PROJECT_ID || '6883392f00125f63c596',
  databaseId: import.meta.env.VITE_APPWRITE_DATABASE_ID || 'sg-security-db',
  
  collections: {
    users: 'users',
    securityEvents: 'security_events',
    securityZones: 'security_zones',
    securityRules: 'security_rules',
    notifications: 'notifications',
    notificationPreferences: 'notification_preferences',
    recordings: 'recordings',
    systemLogs: 'system_logs'
  },
  
  buckets: {
    eventVideos: 'event-videos',
    eventSnapshots: 'event-snapshots'
  },
  
  functions: {
    detectSecurityEvent: 'detect-security-event',
    processVideoBuffer: 'process-video-buffer',
    sendNotifications: 'send-notifications',
    manageRecordings: 'manage-recordings'
  },
  
  teams: {
    superAdmins: 'super-admins',
    admins: 'admins',
    users: 'users'
  }
};

let appwriteClient: Client | null = null;

export function getAppwriteClient(): Client {
  if (!appwriteClient) {
    appwriteClient = new Client()
      .setEndpoint(appwriteConfig.endpoint)
      .setProject(appwriteConfig.projectId);
  }
  return appwriteClient;
}

export const account = new Account(getAppwriteClient());
export const databases = new Databases(getAppwriteClient());
export const storage = new Storage(getAppwriteClient());
export const functions = new Functions(getAppwriteClient());
export const teams = new Teams(getAppwriteClient());
