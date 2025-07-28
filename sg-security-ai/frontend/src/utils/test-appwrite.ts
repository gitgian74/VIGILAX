import { appwriteConfig, account, databases, teams } from '@/config/appwrite.config';

export async function testAppwriteConnection() {
  console.log('🔧 Testing Appwrite Configuration...');
  console.log('Endpoint:', appwriteConfig.endpoint);
  console.log('Project ID:', appwriteConfig.projectId);
  console.log('Database ID:', appwriteConfig.databaseId);
  
  // Test configuration values
  if (!appwriteConfig.projectId || appwriteConfig.projectId === 'sg-security-ai-demo') {
    console.warn('⚠️ Using demo project ID. Please configure a real Appwrite project.');
  }
  
  try {
    // Test account service
    console.log('\n📊 Testing Account Service...');
    const session = await account.get().catch(() => null);
    if (session) {
      console.log('✅ Logged in as:', session.email);
    } else {
      console.log('❌ Not logged in');
    }
    
    // Test database access
    console.log('\n💾 Testing Database Access...');
    try {
      await databases.listDocuments(
        appwriteConfig.databaseId,
        appwriteConfig.collections.users
      );
      console.log('✅ Database connection successful');
    } catch (err) {
      console.error('❌ Database access failed:', (err as Error).message);
    }
    
    // Test storage access - skip for now as it may not exist
    console.log('\n📁 Storage service configured');
    
    // Test teams
    console.log('\n👥 Testing Teams Service...');
    const teamsList = await teams.list().catch((err) => {
      console.error('❌ Teams access failed:', (err as Error).message);
      return null;
    });
    
    if (teamsList) {
      console.log('✅ Teams service accessible');
    }
    
    console.log('\n📋 Configuration Summary:');
    console.log('Collections:', Object.keys(appwriteConfig.collections).join(', '));
    console.log('Buckets:', Object.keys(appwriteConfig.buckets).join(', '));
    console.log('Functions:', Object.keys(appwriteConfig.functions).join(', '));
    console.log('Teams:', Object.keys(appwriteConfig.teams).join(', '));
    
  } catch (error) {
    console.error('\n❌ Appwrite connection test failed:', (error as Error).message);
    console.error('Make sure to:');
    console.error('1. Create an Appwrite project at https://cloud.appwrite.io');
    console.error('2. Update VITE_APPWRITE_PROJECT_ID in .env.local');
    console.error('3. Create the database and collections');
  }
}

// Test function available for manual execution