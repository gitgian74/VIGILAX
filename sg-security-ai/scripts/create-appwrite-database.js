#!/usr/bin/env node

const { Client, Databases, ID, Permission, Role } = require('node-appwrite');
const fs = require('fs');
const path = require('path');

// Load environment variables
const envPath = path.join(__dirname, '../frontend/.env.local');
const envContent = fs.readFileSync(envPath, 'utf-8');
const getEnvVar = (name) => {
  const match = envContent.match(new RegExp(`${name}=(.+)`));
  return match ? match[1].trim() : null;
};

const APPWRITE_ENDPOINT = getEnvVar('VITE_APPWRITE_ENDPOINT');
const APPWRITE_PROJECT_ID = getEnvVar('VITE_APPWRITE_PROJECT_ID');
const APPWRITE_API_KEY = getEnvVar('VITE_APPWRITE_API_KEY');

console.log('🚀 Creating Appwrite Database for SG Security AI\n');
console.log('📋 Configuration:');
console.log(`Endpoint: ${APPWRITE_ENDPOINT}`);
console.log(`Project ID: ${APPWRITE_PROJECT_ID}`);
console.log(`API Key: ${APPWRITE_API_KEY ? '✓ Found' : '✗ Missing'}\n`);

if (!APPWRITE_API_KEY) {
  console.error('❌ API Key not found in .env.local');
  process.exit(1);
}

// Initialize Appwrite client
const client = new Client()
  .setEndpoint(APPWRITE_ENDPOINT)
  .setProject(APPWRITE_PROJECT_ID)
  .setKey(APPWRITE_API_KEY);

const databases = new Databases(client);

async function createDatabase() {
  try {
    console.log('📦 Creating database...');
    const database = await databases.create(
      'sg-security-db',
      'SG Security Database'
    );
    console.log('✅ Database created:', database.$id);
    return database.$id;
  } catch (error) {
    if (error.code === 409) {
      console.log('ℹ️ Database already exists, using existing one');
      return 'sg-security-db';
    }
    throw error;
  }
}

async function createCollection(databaseId, collection) {
  try {
    console.log(`\n📁 Creating collection: ${collection.name}`);
    
    // Create collection
    const col = await databases.createCollection(
      databaseId,
      collection.$id,
      collection.name,
      [
        Permission.read(Role.any()),
        Permission.create(Role.users()),
        Permission.update(Role.users()),
        Permission.delete(Role.users())
      ],
      collection.documentSecurity || true
    );
    
    console.log(`✅ Collection created: ${col.$id}`);
    
    // Create attributes
    for (const attr of collection.attributes) {
      try {
        console.log(`  📝 Creating attribute: ${attr.key}`);
        
        switch (attr.type) {
          case 'string':
            await databases.createStringAttribute(
              databaseId,
              collection.$id,
              attr.key,
              attr.size,
              attr.required,
              attr.default,
              attr.array
            );
            break;
          case 'email':
            await databases.createEmailAttribute(
              databaseId,
              collection.$id,
              attr.key,
              attr.required,
              attr.default,
              attr.array
            );
            break;
          case 'url':
            await databases.createUrlAttribute(
              databaseId,
              collection.$id,
              attr.key,
              attr.required,
              attr.default,
              attr.array
            );
            break;
          case 'integer':
            await databases.createIntegerAttribute(
              databaseId,
              collection.$id,
              attr.key,
              attr.required,
              attr.min,
              attr.max,
              attr.default,
              attr.array
            );
            break;
          case 'double':
            await databases.createFloatAttribute(
              databaseId,
              collection.$id,
              attr.key,
              attr.required,
              attr.min,
              attr.max,
              attr.default,
              attr.array
            );
            break;
          case 'boolean':
            await databases.createBooleanAttribute(
              databaseId,
              collection.$id,
              attr.key,
              attr.required,
              attr.default,
              attr.array
            );
            break;
          case 'datetime':
            await databases.createDatetimeAttribute(
              databaseId,
              collection.$id,
              attr.key,
              attr.required,
              attr.default,
              attr.array
            );
            break;
        }
        
        console.log(`  ✅ Attribute created: ${attr.key}`);
      } catch (error) {
        if (error.code === 409) {
          console.log(`  ℹ️ Attribute ${attr.key} already exists`);
        } else {
          console.error(`  ❌ Error creating attribute ${attr.key}:`, error.message);
        }
      }
    }
    
    // Wait for attributes to be ready before creating indexes
    console.log('  ⏳ Waiting for attributes to be ready...');
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    // Create indexes
    for (const index of collection.indexes || []) {
      try {
        console.log(`  🔍 Creating index: ${index.key}`);
        await databases.createIndex(
          databaseId,
          collection.$id,
          index.key,
          index.type,
          index.attributes,
          index.orders
        );
        console.log(`  ✅ Index created: ${index.key}`);
      } catch (error) {
        if (error.code === 409) {
          console.log(`  ℹ️ Index ${index.key} already exists`);
        } else {
          console.error(`  ❌ Error creating index ${index.key}:`, error.message);
        }
      }
    }
    
  } catch (error) {
    if (error.code === 409) {
      console.log(`ℹ️ Collection ${collection.name} already exists`);
    } else {
      console.error(`❌ Error creating collection ${collection.name}:`, error.message);
    }
  }
}

async function main() {
  try {
    // Create database
    const databaseId = await createDatabase();
    
    // Update .env.local with database ID
    const envContent = fs.readFileSync(envPath, 'utf-8');
    const updatedEnv = envContent.replace(
      'VITE_APPWRITE_DATABASE_ID=sg-security-db',
      `VITE_APPWRITE_DATABASE_ID=${databaseId}`
    );
    fs.writeFileSync(envPath, updatedEnv);
    console.log('\n✅ Updated .env.local with database ID');
    
    // Load schema
    const schemaPath = path.join(__dirname, 'appwrite-schema.json');
    const schema = JSON.parse(fs.readFileSync(schemaPath, 'utf-8'));
    
    // Create collections
    for (const collection of schema.collections) {
      await createCollection(databaseId, collection);
    }
    
    console.log('\n🎉 Database setup complete!');
    console.log('\n📋 Next steps:');
    console.log('1. Create storage buckets in Appwrite Console');
    console.log('2. Create teams (super-admins, admins, users)');
    console.log('3. Deploy cloud functions');
    console.log('4. Run: npm run dev');
    
  } catch (error) {
    console.error('\n❌ Setup failed:', error.message);
    console.error('Make sure your API key has sufficient permissions');
    process.exit(1);
  }
}

main();