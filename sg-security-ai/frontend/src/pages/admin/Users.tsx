import { useState } from 'react'
import { UserPlus, Edit, Trash2, Shield } from 'lucide-react'

export default function Users() {
  const [users] = useState([
    {
      id: '1',
      name: 'Admin User',
      email: 'admin@sg-security.com',
      role: 'super_admin',
      lastActive: '2024-01-25 15:30',
      status: 'active'
    },
    {
      id: '2',
      name: 'Security Guard',
      email: 'guard@sg-security.com',
      role: 'user',
      lastActive: '2024-01-25 14:00',
      status: 'active'
    }
  ])

  const getRoleBadge = (role: string) => {
    const badges = {
      super_admin: 'bg-purple-500/20 text-purple-400 border-purple-500/50',
      admin: 'bg-blue-500/20 text-blue-400 border-blue-500/50',
      user: 'bg-gray-500/20 text-gray-400 border-gray-500/50'
    }
    return badges[role as keyof typeof badges] || badges.user
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold">User Management</h1>
        <button className="btn-primary flex items-center space-x-2">
          <UserPlus className="h-4 w-4" />
          <span>Add User</span>
        </button>
      </div>

      <div className="card">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-dark-border">
                <th className="text-left py-3 px-4">User</th>
                <th className="text-left py-3 px-4">Role</th>
                <th className="text-left py-3 px-4">Last Active</th>
                <th className="text-left py-3 px-4">Status</th>
                <th className="text-left py-3 px-4">Actions</th>
              </tr>
            </thead>
            <tbody>
              {users.map((user) => (
                <tr key={user.id} className="border-b border-dark-border/50">
                  <td className="py-3 px-4">
                    <div>
                      <p className="font-medium">{user.name}</p>
                      <p className="text-sm text-gray-400">{user.email}</p>
                    </div>
                  </td>
                  <td className="py-3 px-4">
                    <span className={`inline-flex items-center space-x-1 px-2 py-1 rounded-full text-xs border ${getRoleBadge(user.role)}`}>
                      <Shield className="h-3 w-3" />
                      <span>{user.role.replace('_', ' ')}</span>
                    </span>
                  </td>
                  <td className="py-3 px-4 text-sm text-gray-400">
                    {user.lastActive}
                  </td>
                  <td className="py-3 px-4">
                    <span className={`inline-flex px-2 py-1 rounded-full text-xs ${
                      user.status === 'active' 
                        ? 'bg-green-500/20 text-green-400' 
                        : 'bg-gray-500/20 text-gray-400'
                    }`}>
                      {user.status}
                    </span>
                  </td>
                  <td className="py-3 px-4">
                    <div className="flex items-center space-x-2">
                      <button className="p-1 hover:bg-dark-border rounded">
                        <Edit className="h-4 w-4" />
                      </button>
                      <button className="p-1 hover:bg-red-500/20 hover:text-red-400 rounded">
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}