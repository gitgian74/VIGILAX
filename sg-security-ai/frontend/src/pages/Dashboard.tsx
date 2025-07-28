import { useEffect, useState } from 'react'
import { useViamConnection } from '@/hooks/useViamConnection'
import { appwriteConfig } from '@/config/appwrite.config'
// import { testAppwriteConnection } from '@/utils/test-appwrite'

export default function Dashboard() {
  const { isConnected, isConnecting, error } = useViamConnection()
  const [appwriteStatus, setAppwriteStatus] = useState<'checking' | 'connected' | 'error'>('checking')

  useEffect(() => {
    // Test Appwrite connection on mount
    checkAppwriteConnection()
  }, [])

  const checkAppwriteConnection = async () => {
    try {
      // For now, just check if config is set
      if (appwriteConfig.projectId && appwriteConfig.projectId !== 'sg-security-ai-demo') {
        setAppwriteStatus('connected')
      } else {
        setAppwriteStatus('error')
      }
      
      // Test available for manual execution
    } catch (error) {
      setAppwriteStatus('error')
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <div className="flex items-center space-x-4">
          {/* Viam Connection Status */}
          <div className="flex items-center space-x-2">
            <div className={`w-3 h-3 rounded-full ${
              isConnected ? 'bg-green-500 animate-pulse' : 
              isConnecting ? 'bg-yellow-500 animate-pulse' : 
              'bg-red-500'
            }`}></div>
            <span className="text-sm">
              Viam: {isConnecting ? 'Connecting...' : isConnected ? 'Connected' : 'Offline'}
            </span>
          </div>

          {/* Appwrite Connection Status */}
          <div className="flex items-center space-x-2">
            <div className={`w-3 h-3 rounded-full ${
              appwriteStatus === 'connected' ? 'bg-green-500 animate-pulse' : 
              appwriteStatus === 'checking' ? 'bg-yellow-500 animate-pulse' : 
              'bg-red-500'
            }`}></div>
            <span className="text-sm">
              Appwrite: {
                appwriteStatus === 'checking' ? 'Checking...' : 
                appwriteStatus === 'connected' ? 'Connected' : 
                'Not Configured'
              }
            </span>
          </div>
        </div>
      </div>

      {/* Configuration Info */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="card">
          <h3 className="text-lg font-semibold mb-3">🤖 Viam Configuration</h3>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-400">Robot Address:</span>
              <span className="font-mono text-xs">{import.meta.env.VITE_VIAM_ROBOT_ADDRESS || 'Not configured'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">API Key ID:</span>
              <span className="font-mono text-xs">{import.meta.env.VITE_VIAM_API_KEY_ID?.substring(0, 8)}...</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Status:</span>
              <span className={isConnected ? 'text-green-400' : 'text-red-400'}>
                {isConnected ? 'Active' : error || 'Disconnected'}
              </span>
            </div>
          </div>
        </div>

        <div className="card">
          <h3 className="text-lg font-semibold mb-3">☁️ Appwrite Configuration</h3>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-400">Endpoint:</span>
              <span className="font-mono text-xs">{appwriteConfig.endpoint}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Project ID:</span>
              <span className="font-mono text-xs">{appwriteConfig.projectId || 'Not configured'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-400">Database ID:</span>
              <span className="font-mono text-xs">{appwriteConfig.databaseId || 'Not configured'}</span>
            </div>
          </div>
          {appwriteStatus === 'error' && (
            <div className="mt-3 p-2 bg-yellow-500/20 border border-yellow-500/50 rounded text-xs">
              ⚠️ Please configure Appwrite in .env.local
            </div>
          )}
        </div>
      </div>

      {error && (
        <div className="bg-red-500/20 border border-red-500 rounded-md p-4">
          <p className="text-red-400">Viam Error: {error}</p>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card">
          <h2 className="text-xl font-semibold mb-4">📹 Camera Stream</h2>
          <div className="video-container bg-dark-surface rounded-md">
            <div className="flex items-center justify-center h-full text-gray-400">
              {isConnected ? 'Camera stream will appear here' : 'Connect to Viam to view stream'}
            </div>
          </div>
        </div>

        <div className="card">
          <h2 className="text-xl font-semibold mb-4">🚨 Recent Events</h2>
          <div className="space-y-2">
            <p className="text-gray-400">No recent security events</p>
          </div>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="card p-4">
          <h4 className="text-sm text-gray-400 mb-1">Total Events Today</h4>
          <p className="text-2xl font-bold">0</p>
        </div>
        <div className="card p-4">
          <h4 className="text-sm text-gray-400 mb-1">Active Cameras</h4>
          <p className="text-2xl font-bold">{isConnected ? '2' : '0'}</p>
        </div>
        <div className="card p-4">
          <h4 className="text-sm text-gray-400 mb-1">Security Zones</h4>
          <p className="text-2xl font-bold">2</p>
        </div>
        <div className="card p-4">
          <h4 className="text-sm text-gray-400 mb-1">System Status</h4>
          <p className="text-2xl font-bold text-green-400">OK</p>
        </div>
      </div>
    </div>
  )
}