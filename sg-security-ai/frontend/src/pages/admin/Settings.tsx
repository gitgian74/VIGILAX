import { useState } from 'react'
import { Save, Bell, Camera, Shield, Database, Wifi } from 'lucide-react'

export default function Settings() {
  const [activeTab, setActiveTab] = useState('general')

  const tabs = [
    { id: 'general', name: 'General', icon: Shield },
    { id: 'cameras', name: 'Cameras', icon: Camera },
    { id: 'notifications', name: 'Notifications', icon: Bell },
    { id: 'database', name: 'Database', icon: Database },
    { id: 'network', name: 'Network', icon: Wifi },
  ]

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Settings</h1>
        <button className="btn-primary flex items-center space-x-2">
          <Save className="h-4 w-4" />
          <span>Save Changes</span>
        </button>
      </div>

      <div className="flex space-x-6">
        {/* Sidebar */}
        <div className="w-64">
          <nav className="space-y-1">
            {tabs.map((tab) => {
              const Icon = tab.icon
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`w-full flex items-center space-x-3 px-4 py-2 rounded-md transition-colors ${
                    activeTab === tab.id
                      ? 'bg-primary/20 text-primary border-l-2 border-primary'
                      : 'hover:bg-dark-surface text-gray-400'
                  }`}
                >
                  <Icon className="h-5 w-5" />
                  <span>{tab.name}</span>
                </button>
              )
            })}
          </nav>
        </div>

        {/* Content */}
        <div className="flex-1">
          <div className="card">
            {activeTab === 'general' && (
              <div className="space-y-6">
                <h3 className="text-lg font-semibold">General Settings</h3>
                
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      System Name
                    </label>
                    <input
                      type="text"
                      className="input"
                      defaultValue="SG Security AI"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Time Zone
                    </label>
                    <select className="input">
                      <option>UTC</option>
                      <option>Europe/Rome</option>
                      <option>America/New_York</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Video Buffer Duration (minutes)
                    </label>
                    <input
                      type="number"
                      className="input"
                      defaultValue="1"
                      min="1"
                      max="10"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      ML Confidence Threshold
                    </label>
                    <input
                      type="number"
                      className="input"
                      defaultValue="0.7"
                      min="0.1"
                      max="1"
                      step="0.1"
                    />
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'cameras' && (
              <div className="space-y-6">
                <h3 className="text-lg font-semibold">Camera Configuration</h3>
                
                <div className="space-y-4">
                  <div className="p-4 border border-dark-border rounded-md">
                    <h4 className="font-medium mb-3">Camera Esterna</h4>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm text-gray-400 mb-1">Name</label>
                        <input type="text" className="input" defaultValue="camera-1" />
                      </div>
                      <div>
                        <label className="block text-sm text-gray-400 mb-1">Display Name</label>
                        <input type="text" className="input" defaultValue="Camera Esterna" />
                      </div>
                      <div>
                        <label className="block text-sm text-gray-400 mb-1">Resolution</label>
                        <select className="input">
                          <option>1920x1080</option>
                          <option>1280x720</option>
                          <option>640x480</option>
                        </select>
                      </div>
                      <div>
                        <label className="block text-sm text-gray-400 mb-1">Frame Rate</label>
                        <input type="number" className="input" defaultValue="30" />
                      </div>
                    </div>
                  </div>

                  <div className="p-4 border border-dark-border rounded-md">
                    <h4 className="font-medium mb-3">Camera Interna</h4>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm text-gray-400 mb-1">Name</label>
                        <input type="text" className="input" defaultValue="camera-2" />
                      </div>
                      <div>
                        <label className="block text-sm text-gray-400 mb-1">Display Name</label>
                        <input type="text" className="input" defaultValue="Camera Interna" />
                      </div>
                      <div>
                        <label className="block text-sm text-gray-400 mb-1">Resolution</label>
                        <select className="input">
                          <option>1920x1080</option>
                          <option>1280x720</option>
                          <option>640x480</option>
                        </select>
                      </div>
                      <div>
                        <label className="block text-sm text-gray-400 mb-1">Frame Rate</label>
                        <input type="number" className="input" defaultValue="30" />
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'notifications' && (
              <div className="space-y-6">
                <h3 className="text-lg font-semibold">Notification Settings</h3>
                
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">Email Notifications</p>
                      <p className="text-sm text-gray-400">Send alerts via email</p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input type="checkbox" className="sr-only peer" defaultChecked />
                      <div className="w-11 h-6 bg-gray-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
                    </label>
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">SMS Notifications</p>
                      <p className="text-sm text-gray-400">Send critical alerts via SMS</p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input type="checkbox" className="sr-only peer" />
                      <div className="w-11 h-6 bg-gray-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
                    </label>
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">Daily Reports</p>
                      <p className="text-sm text-gray-400">Receive daily security summaries</p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input type="checkbox" className="sr-only peer" />
                      <div className="w-11 h-6 bg-gray-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
                    </label>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'database' && (
              <div className="space-y-6">
                <h3 className="text-lg font-semibold">Database Settings</h3>
                
                <div className="space-y-4">
                  <div className="p-4 bg-dark-surface rounded-md">
                    <p className="text-sm text-gray-400 mb-2">Database Status</p>
                    <p className="text-green-400">Connected</p>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Retention Period (days)
                    </label>
                    <input
                      type="number"
                      className="input"
                      defaultValue="30"
                      min="7"
                      max="365"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Auto-backup Frequency
                    </label>
                    <select className="input">
                      <option>Daily</option>
                      <option>Weekly</option>
                      <option>Monthly</option>
                    </select>
                  </div>

                  <button className="btn-secondary">
                    Export Database Backup
                  </button>
                </div>
              </div>
            )}

            {activeTab === 'network' && (
              <div className="space-y-6">
                <h3 className="text-lg font-semibold">Network Settings</h3>
                
                <div className="space-y-4">
                  <div className="p-4 bg-dark-surface rounded-md">
                    <p className="text-sm text-gray-400 mb-2">Viam Connection</p>
                    <p className="text-green-400">Connected to ssa-locaratow-main</p>
                  </div>

                  <div className="p-4 bg-dark-surface rounded-md">
                    <p className="text-sm text-gray-400 mb-2">Appwrite Connection</p>
                    <p className="text-yellow-400">Configuration Required</p>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      API Timeout (seconds)
                    </label>
                    <input
                      type="number"
                      className="input"
                      defaultValue="30"
                      min="5"
                      max="120"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Max Retry Attempts
                    </label>
                    <input
                      type="number"
                      className="input"
                      defaultValue="3"
                      min="0"
                      max="10"
                    />
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}