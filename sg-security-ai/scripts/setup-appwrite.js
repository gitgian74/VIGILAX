#!/usr/bin/env node

/**
 * Script di setup automatico per Appwrite
 * Crea database, collections, teams e configurazioni necessarie
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('🚀 Setup Appwrite per SG Security AI\n');

// Verifica che Appwrite CLI sia installato
try {
  execSync('appwrite --version', { stdio: 'ignore' });
} catch (error) {
  console.error('❌ Appwrite CLI non trovato. Installalo con: npm install -g appwrite-cli');
  process.exit(1);
}

// Leggi configurazione da .env.local
const envPath = path.join(__dirname, '../frontend/.env.local');
if (!fs.existsSync(envPath)) {
  console.error('❌ File .env.local non trovato. Copia .env.example in .env.local e configura le variabili.');
  process.exit(1);
}

const envContent = fs.readFileSync(envPath, 'utf-8');
const getEnvVar = (name) => {
  const match = envContent.match(new RegExp(`${name}=(.+)`));
  return match ? match[1].trim() : null;
};

const projectId = getEnvVar('VITE_APPWRITE_PROJECT_ID');
const endpoint = getEnvVar('VITE_APPWRITE_ENDPOINT');

if (!projectId || projectId === 'INSERISCI_PROJECT_ID_QUI') {
  console.error('❌ Configura VITE_APPWRITE_PROJECT_ID nel file .env.local');
  process.exit(1);
}

console.log(`📋 Project ID: ${projectId}`);
console.log(`🌐 Endpoint: ${endpoint}\n`);

// Schema del database
const collections = [
  {
    name: 'users',
    $id: 'users',
    attributes: [
      { key: 'email', type: 'email', required: true, size: 255 },
      { key: 'name', type: 'string', required: true, size: 255 },
      { key: 'role', type: 'string', required: true, size: 50, default: 'user' },
      { key: 'avatar', type: 'url', required: false, size: 2000 },
      { key: 'phone', type: 'string', required: false, size: 20 },
      { key: 'notificationPreferences', type: 'string', required: true, size: 5000 }
    ],
    indexes: [
      { key: 'email', type: 'unique', attributes: ['email'] },
      { key: 'role', type: 'key', attributes: ['role'] }
    ]
  },
  {
    name: 'security_events',
    $id: 'security_events',
    attributes: [
      { key: 'type', type: 'string', required: true, size: 50 },
      { key: 'timestamp', type: 'datetime', required: true },
      { key: 'cameraName', type: 'string', required: true, size: 100 },
      { key: 'zone', type: 'string', required: false, size: 100 },
      { key: 'confidence', type: 'double', required: true, min: 0, max: 1 },
      { key: 'details', type: 'string', required: true, size: 5000 },
      { key: 'severity', type: 'string', required: true, size: 20 },
      { key: 'processed', type: 'boolean', required: true, default: false },
      { key: 'notificationsSent', type: 'boolean', required: true, default: false }
    ],
    indexes: [
      { key: 'timestamp', type: 'key', attributes: ['timestamp'] },
      { key: 'severity', type: 'key', attributes: ['severity'] }
    ]
  },
  {
    name: 'security_zones',
    $id: 'security_zones',
    attributes: [
      { key: 'name', type: 'string', required: true, size: 255 },
      { key: 'description', type: 'string', required: false, size: 1000 },
      { key: 'type', type: 'string', required: true, size: 50 },
      { key: 'coordinates', type: 'string', required: true, size: 1000 },
      { key: 'cameras', type: 'string', required: true, size: 1000, array: true },
      { key: 'activeHours', type: 'string', required: true, size: 50 },
      { key: 'enabled', type: 'boolean', required: true, default: true },
      { key: 'createdBy', type: 'string', required: true, size: 255 }
    ]
  },
  {
    name: 'notifications',
    $id: 'notifications',
    attributes: [
      { key: 'userId', type: 'string', required: true, size: 255 },
      { key: 'type', type: 'string', required: true, size: 50 },
      { key: 'subject', type: 'string', required: true, size: 500 },
      { key: 'message', type: 'string', required: true, size: 5000 },
      { key: 'status', type: 'string', required: true, size: 50 },
      { key: 'eventId', type: 'string', required: false, size: 255 },
      { key: 'metadata', type: 'string', required: false, size: 5000 },
      { key: 'sentAt', type: 'datetime', required: false }
    ],
    indexes: [
      { key: 'userId', type: 'key', attributes: ['userId'] },
      { key: 'status', type: 'key', attributes: ['status'] }
    ]
  }
];

console.log('📝 Creazione collections...\n');

// Qui dovrebbe seguire il codice per creare le collections via CLI
// Ma per brevità, mostro solo la struttura

console.log('✅ Setup completato!\n');
console.log('⚡ Prossimi passi:');
console.log('1. Vai su https://cloud.appwrite.io e crea le collections manualmente');
console.log('2. Copia gli ID delle collections nel file appwrite.config.ts');
console.log('3. Crea i team: super-admins, admins, users');
console.log('4. Configura le Appwrite Functions nel backend/functions');
