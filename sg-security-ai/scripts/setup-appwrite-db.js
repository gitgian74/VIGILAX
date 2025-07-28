#!/usr/bin/env node

/**
 * Script di setup del database Appwrite per SG Security AI
 * Crea tutte le collections, attributi e indici necessari
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('🚀 Setup Database Appwrite per SG Security AI\n');

// Collections schema completo
const collections = [
  {
    $id: 'users',
    name: 'Users',
    documentSecurity: true,
    enabled: true,
    attributes: [
      { key: 'email', type: 'email', required: true, size: 255 },
      { key: 'name', type: 'string', required: true, size: 255 },
      { key: 'role', type: 'string', required: true, size: 50, default: 'user' },
      { key: 'avatar', type: 'url', required: false, size: 2000 },
      { key: 'phone', type: 'string', required: false, size: 20 },
      { key: 'notificationPreferences', type: 'string', required: true, size: 5000, default: '{}' }
    ],
    indexes: [
      { key: 'email_idx', type: 'unique', attributes: ['email'] },
      { key: 'role_idx', type: 'key', attributes: ['role'] }
    ]
  },
  {
    $id: 'security_events',
    name: 'Security Events',
    documentSecurity: true,
    enabled: true,
    attributes: [
      { key: 'type', type: 'string', required: true, size: 50 },
      { key: 'timestamp', type: 'datetime', required: true },
      { key: 'cameraName', type: 'string', required: true, size: 100 },
      { key: 'cameraDisplayName', type: 'string', required: true, size: 100 },
      { key: 'zone', type: 'string', required: false, size: 100 },
      { key: 'confidence', type: 'double', required: true, min: 0, max: 1 },
      { key: 'severity', type: 'string', required: true, size: 20 },
      { key: 'details', type: 'string', required: true, size: 5000 },
      { key: 'videoBufferId', type: 'string', required: false, size: 255 },
      { key: 'snapshotId', type: 'string', required: false, size: 255 },
      { key: 'processed', type: 'boolean', required: true, default: false },
      { key: 'notificationsSent', type: 'boolean', required: true, default: false },
      { key: 'acknowledgedBy', type: 'string', required: false, size: 255 },
      { key: 'acknowledgedAt', type: 'datetime', required: false }
    ],
    indexes: [
      { key: 'timestamp_idx', type: 'key', attributes: ['timestamp'], orders: ['DESC'] },
      { key: 'type_camera_idx', type: 'key', attributes: ['type', 'cameraName'] },
      { key: 'severity_idx', type: 'key', attributes: ['severity'] },
      { key: 'processed_idx', type: 'key', attributes: ['processed'] }
    ]
  },
  {
    $id: 'security_zones',
    name: 'Security Zones',
    documentSecurity: true,
    enabled: true,
    attributes: [
      { key: 'name', type: 'string', required: true, size: 255 },
      { key: 'description', type: 'string', required: false, size: 1000 },
      { key: 'type', type: 'string', required: true, size: 50 },
      { key: 'coordinates', type: 'string', required: true, size: 1000 },
      { key: 'cameras', type: 'string', required: true, size: 1000, array: true },
      { key: 'activeHours', type: 'string', required: true, size: 50 },
      { key: 'enabled', type: 'boolean', required: true, default: true },
      { key: 'rules', type: 'string', required: false, size: 5000, default: '[]' },
      { key: 'createdBy', type: 'string', required: true, size: 255 }
    ],
    indexes: [
      { key: 'type_idx', type: 'key', attributes: ['type'] },
      { key: 'enabled_idx', type: 'key', attributes: ['enabled'] }
    ]
  },
  {
    $id: 'security_rules',
    name: 'Security Rules',
    documentSecurity: true,
    enabled: true,
    attributes: [
      { key: 'name', type: 'string', required: true, size: 255 },
      { key: 'description', type: 'string', required: false, size: 1000 },
      { key: 'type', type: 'string', required: true, size: 50 },
      { key: 'conditions', type: 'string', required: true, size: 5000 },
      { key: 'actions', type: 'string', required: true, size: 1000 },
      { key: 'severity', type: 'string', required: true, size: 20 },
      { key: 'enabled', type: 'boolean', required: true, default: true },
      { key: 'createdBy', type: 'string', required: true, size: 255 }
    ],
    indexes: [
      { key: 'type_idx', type: 'key', attributes: ['type'] },
      { key: 'enabled_idx', type: 'key', attributes: ['enabled'] },
      { key: 'severity_idx', type: 'key', attributes: ['severity'] }
    ]
  },
  {
    $id: 'notifications',
    name: 'Notifications',
    documentSecurity: true,
    enabled: true,
    attributes: [
      { key: 'userId', type: 'string', required: true, size: 255 },
      { key: 'type', type: 'string', required: true, size: 50 },
      { key: 'subject', type: 'string', required: true, size: 500 },
      { key: 'message', type: 'string', required: true, size: 5000 },
      { key: 'status', type: 'string', required: true, size: 50, default: 'pending' },
      { key: 'eventId', type: 'string', required: false, size: 255 },
      { key: 'metadata', type: 'string', required: false, size: 5000 },
      { key: 'sentAt', type: 'datetime', required: false }
    ],
    indexes: [
      { key: 'userId_idx', type: 'key', attributes: ['userId'] },
      { key: 'status_idx', type: 'key', attributes: ['status'] },
      { key: 'type_idx', type: 'key', attributes: ['type'] }
    ]
  },
  {
    $id: 'recordings',
    name: 'Recordings',
    documentSecurity: true,
    enabled: true,
    attributes: [
      { key: 'cameraName', type: 'string', required: true, size: 100 },
      { key: 'type', type: 'string', required: true, size: 50 },
      { key: 'startTime', type: 'datetime', required: true },
      { key: 'endTime', type: 'datetime', required: true },
      { key: 'filePath', type: 'string', required: true, size: 500 },
      { key: 'fileSize', type: 'integer', required: true, min: 0 },
      { key: 'eventId', type: 'string', required: false, size: 255 },
      { key: 'isCloudStored', type: 'boolean', required: true, default: false },
      { key: 'cloudUrl', type: 'url', required: false, size: 2000 },
      { key: 'thumbnailUrl', type: 'url', required: false, size: 2000 }
    ],
    indexes: [
      { key: 'camera_time_idx', type: 'key', attributes: ['cameraName', 'startTime'], orders: ['ASC', 'DESC'] },
      { key: 'type_idx', type: 'key', attributes: ['type'] },
      { key: 'eventId_idx', type: 'key', attributes: ['eventId'] }
    ]
  },
  {
    $id: 'system_logs',
    name: 'System Logs',
    documentSecurity: true,
    enabled: true,
    attributes: [
      { key: 'level', type: 'string', required: true, size: 20 },
      { key: 'module', type: 'string', required: true, size: 100 },
      { key: 'message', type: 'string', required: true, size: 5000 },
      { key: 'details', type: 'string', required: false, size: 10000 },
      { key: 'userId', type: 'string', required: false, size: 255 },
      { key: 'timestamp', type: 'datetime', required: true }
    ],
    indexes: [
      { key: 'timestamp_idx', type: 'key', attributes: ['timestamp'], orders: ['DESC'] },
      { key: 'level_idx', type: 'key', attributes: ['level'] },
      { key: 'module_idx', type: 'key', attributes: ['module'] }
    ]
  }
];

// Storage buckets
const buckets = [
  {
    $id: 'event-videos',
    name: 'Event Videos',
    permissions: ['read("any")', 'create("users")', 'update("users")', 'delete("users")'],
    fileSecurity: true,
    enabled: true,
    maximumFileSize: 104857600, // 100MB
    allowedFileExtensions: ['mp4', 'avi', 'mov', 'mkv'],
    compression: 'none',
    encryption: true,
    antivirus: true
  },
  {
    $id: 'event-snapshots',
    name: 'Event Snapshots',
    permissions: ['read("any")', 'create("users")', 'update("users")', 'delete("users")'],
    fileSecurity: true,
    enabled: true,
    maximumFileSize: 10485760, // 10MB
    allowedFileExtensions: ['jpg', 'jpeg', 'png', 'webp'],
    compression: 'gzip',
    encryption: true,
    antivirus: true
  }
];

// Teams (Roles)
const teams = [
  {
    $id: 'super-admins',
    name: 'Super Administrators',
    roles: ['owner', 'create', 'read', 'update', 'delete']
  },
  {
    $id: 'admins',
    name: 'Administrators',
    roles: ['create', 'read', 'update', 'delete']
  },
  {
    $id: 'users',
    name: 'Standard Users',
    roles: ['read']
  }
];

console.log('📋 Schema Summary:');
console.log(`- ${collections.length} Collections`);
console.log(`- ${buckets.length} Storage Buckets`);
console.log(`- ${teams.length} Teams\n`);

console.log('⚡ Instructions for Appwrite Setup:\n');

console.log('1. Go to https://cloud.appwrite.io and create a new project');
console.log('2. Copy the Project ID and update VITE_APPWRITE_PROJECT_ID in .env.local');
console.log('3. Create a new Database and copy its ID to VITE_APPWRITE_DATABASE_ID');
console.log('4. Create an API Key with full permissions for initial setup');
console.log('5. Use the Appwrite Console to create the collections with the schema above\n');

console.log('📁 Collections to create:');
collections.forEach(col => {
  console.log(`\n   ${col.name} (${col.$id}):`);
  console.log(`   - ${col.attributes.length} attributes`);
  console.log(`   - ${col.indexes.length} indexes`);
});

console.log('\n\n💾 Storage Buckets to create:');
buckets.forEach(bucket => {
  console.log(`\n   ${bucket.name} (${bucket.$id}):`);
  console.log(`   - Max file size: ${bucket.maximumFileSize / 1024 / 1024}MB`);
  console.log(`   - Extensions: ${bucket.allowedFileExtensions.join(', ')}`);
});

console.log('\n\n👥 Teams to create:');
teams.forEach(team => {
  console.log(`   - ${team.name} (${team.$id})`);
});

console.log('\n\n✅ Once setup is complete, run: npm run dev');

// Export schema for other tools
const schemaPath = path.join(__dirname, 'appwrite-schema.json');
fs.writeFileSync(schemaPath, JSON.stringify({ collections, buckets, teams }, null, 2));
console.log(`\n📄 Schema exported to: ${schemaPath}`);