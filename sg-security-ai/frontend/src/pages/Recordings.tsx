import { useState } from 'react'
import { Calendar, Play, Download, Trash2 } from 'lucide-react'

export default function Recordings() {
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0])
  const [selectedCamera, setSelectedCamera] = useState('all')

  // Mock data - will be replaced with real data
  const recordings = [
    {
      id: '1',
      cameraName: 'camera-1',
      cameraDisplayName: 'Camera Esterna',
      type: 'event',
      startTime: '2024-01-25 14:30:00',
      duration: '00:05:23',
      size: '125 MB',
      eventType: 'motion_detected'
    },
    {
      id: '2',
      cameraName: 'camera-2',
      cameraDisplayName: 'Camera Interna',
      type: 'continuous',
      startTime: '2024-01-25 12:00:00',
      duration: '01:00:00',
      size: '1.2 GB',
      eventType: null
    }
  ]

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">Recordings</h1>
        <div className="flex items-center space-x-4">
          <select
            value={selectedCamera}
            onChange={(e) => setSelectedCamera(e.target.value)}
            className="input"
          >
            <option value="all">All Cameras</option>
            <option value="camera-1">Camera Esterna</option>
            <option value="camera-2">Camera Interna</option>
          </select>

          <input
            type="date"
            value={selectedDate}
            onChange={(e) => setSelectedDate(e.target.value)}
            className="input"
          />
        </div>
      </div>

      <div className="grid gap-4">
        {recordings.map((recording) => (
          <div key={recording.id} className="card hover:border-primary/50 transition-colors">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-4">
                <div className="w-32 h-20 bg-dark-surface rounded flex items-center justify-center">
                  <Play className="h-8 w-8 text-gray-400" />
                </div>
                
                <div>
                  <h3 className="font-semibold">{recording.cameraDisplayName}</h3>
                  <p className="text-sm text-gray-400">
                    <Calendar className="inline h-3 w-3 mr-1" />
                    {recording.startTime} • Duration: {recording.duration}
                  </p>
                  <p className="text-xs text-gray-500">
                    {recording.type === 'event' ? `Event: ${recording.eventType}` : 'Continuous Recording'}
                    • Size: {recording.size}
                  </p>
                </div>
              </div>

              <div className="flex items-center space-x-2">
                <button className="btn-secondary p-2">
                  <Play className="h-4 w-4" />
                </button>
                <button className="btn-secondary p-2">
                  <Download className="h-4 w-4" />
                </button>
                <button className="btn-secondary p-2 hover:bg-red-500/20 hover:text-red-400">
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>

      {recordings.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-400">No recordings found for the selected date</p>
        </div>
      )}
    </div>
  )
}