import { LineChart, Line, BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

export default function Analytics() {
  // Mock data - will be replaced with real data
  const eventsByHour = [
    { hour: '00:00', events: 2 },
    { hour: '04:00', events: 1 },
    { hour: '08:00', events: 5 },
    { hour: '12:00', events: 3 },
    { hour: '16:00', events: 7 },
    { hour: '20:00', events: 4 },
  ]

  const eventsByType = [
    { name: 'Motion Detected', value: 45, color: '#0ea5e9' },
    { name: 'Loitering', value: 20, color: '#10b981' },
    { name: 'Intrusion', value: 15, color: '#f59e0b' },
    { name: 'Gate Activity', value: 20, color: '#8b5cf6' },
  ]

  const cameraActivity = [
    { camera: 'External', events: 65 },
    { camera: 'Internal', events: 35 },
  ]

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Analytics</h1>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="card p-4">
          <h4 className="text-sm text-gray-400 mb-1">Total Events (24h)</h4>
          <p className="text-3xl font-bold">127</p>
          <p className="text-xs text-green-400">+12% from yesterday</p>
        </div>
        <div className="card p-4">
          <h4 className="text-sm text-gray-400 mb-1">Critical Alerts</h4>
          <p className="text-3xl font-bold text-red-400">3</p>
          <p className="text-xs text-gray-400">Requires attention</p>
        </div>
        <div className="card p-4">
          <h4 className="text-sm text-gray-400 mb-1">Avg Response Time</h4>
          <p className="text-3xl font-bold">2.5s</p>
          <p className="text-xs text-green-400">-0.3s improvement</p>
        </div>
        <div className="card p-4">
          <h4 className="text-sm text-gray-400 mb-1">System Uptime</h4>
          <p className="text-3xl font-bold">99.9%</p>
          <p className="text-xs text-gray-400">Last 30 days</p>
        </div>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Events Timeline */}
        <div className="card">
          <h3 className="text-lg font-semibold mb-4">Events Timeline (24h)</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={eventsByHour}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="hour" stroke="#9CA3AF" />
              <YAxis stroke="#9CA3AF" />
              <Tooltip 
                contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151' }}
                labelStyle={{ color: '#9CA3AF' }}
              />
              <Line type="monotone" dataKey="events" stroke="#0ea5e9" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Events by Type */}
        <div className="card">
          <h3 className="text-lg font-semibold mb-4">Events by Type</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={eventsByType}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {eventsByType.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Camera Activity */}
        <div className="card">
          <h3 className="text-lg font-semibold mb-4">Camera Activity</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={cameraActivity}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="camera" stroke="#9CA3AF" />
              <YAxis stroke="#9CA3AF" />
              <Tooltip 
                contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151' }}
                labelStyle={{ color: '#9CA3AF' }}
              />
              <Bar dataKey="events" fill="#10b981" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Heatmap Placeholder */}
        <div className="card">
          <h3 className="text-lg font-semibold mb-4">Activity Heatmap</h3>
          <div className="h-[300px] bg-dark-surface rounded flex items-center justify-center">
            <p className="text-gray-400">Heatmap visualization coming soon</p>
          </div>
        </div>
      </div>

      {/* Recent Alerts Table */}
      <div className="card">
        <h3 className="text-lg font-semibold mb-4">Recent High-Priority Events</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-dark-border">
                <th className="text-left py-2 px-4">Time</th>
                <th className="text-left py-2 px-4">Type</th>
                <th className="text-left py-2 px-4">Camera</th>
                <th className="text-left py-2 px-4">Severity</th>
                <th className="text-left py-2 px-4">Status</th>
              </tr>
            </thead>
            <tbody>
              <tr className="border-b border-dark-border/50">
                <td className="py-2 px-4">16:45</td>
                <td className="py-2 px-4">Intrusion Detected</td>
                <td className="py-2 px-4">Camera Esterna</td>
                <td className="py-2 px-4"><span className="text-red-400">Critical</span></td>
                <td className="py-2 px-4"><span className="text-green-400">Resolved</span></td>
              </tr>
              <tr className="border-b border-dark-border/50">
                <td className="py-2 px-4">14:30</td>
                <td className="py-2 px-4">Unauthorized Access</td>
                <td className="py-2 px-4">Camera Interna</td>
                <td className="py-2 px-4"><span className="text-orange-400">High</span></td>
                <td className="py-2 px-4"><span className="text-yellow-400">Pending</span></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}