import { create } from 'zustand'
import { account, databases, teams } from '@/config/appwrite.config'
import { User, AuthState } from '@/types'
import { ID } from 'appwrite'

interface AuthStore extends AuthState {
  login: (email: string, password: string) => Promise<void>
  logout: () => Promise<void>
  register: (email: string, password: string, name: string) => Promise<void>
  checkAuth: () => Promise<void>
  updateUser: (user: Partial<User>) => void
}

export const useAuth = create<AuthStore>((set) => ({
  user: null,
  isAuthenticated: false,
  isLoading: true,
  error: null,

  login: async (email: string, password: string) => {
    try {
      set({ isLoading: true, error: null })
      
      // Login con Appwrite
      await account.createEmailSession(email, password)
      
      // Ottieni dati utente
      const accountData = await account.get()
      const prefs = await account.getPrefs()
      
      // Ottieni ruolo utente dal team
      const userTeams = await teams.list()
      let role: User['role'] = 'user'
      
      if (userTeams.teams.some(t => t.$id === 'super-admins')) {
        role = 'super_admin'
      } else if (userTeams.teams.some(t => t.$id === 'admins')) {
        role = 'admin'
      }
      
      const user: User = {
        id: accountData.$id,
        email: accountData.email,
        name: accountData.name,
        role,
        avatar: prefs.avatar,
        phone: prefs.phone,
        notificationPreferences: prefs.notificationPreferences || {
          email: true,
          sms: false,
          securityAlerts: true,
          dailyReports: false,
        },
        createdAt: new Date(accountData.$createdAt),
        updatedAt: new Date(accountData.$updatedAt),
      }
      
      set({ user, isAuthenticated: true, isLoading: false })
    } catch (error) {
      console.error('Login error:', error)
      set({ 
        error: (error as Error).message || 'Errore durante il login', 
        isLoading: false,
        isAuthenticated: false 
      })
      throw error
    }
  },

  logout: async () => {
    try {
      await account.deleteSession('current')
      set({ user: null, isAuthenticated: false })
    } catch (error) {
      console.error('Logout error:', error)
    }
  },

  register: async (email: string, password: string, name: string) => {
    try {
      set({ isLoading: true, error: null })
      
      // Crea account
      await account.create(ID.unique(), email, password, name)
      
      // Login automatico
      await account.createEmailSession(email, password)
      
      // Crea profilo utente nel database
      const accountData = await account.get()
      
      await databases.createDocument(
        import.meta.env.VITE_APPWRITE_DATABASE_ID,
        'users',
        accountData.$id,
        {
          email,
          name,
          role: 'user',
          notificationPreferences: JSON.stringify({
            email: true,
            sms: false,
            securityAlerts: true,
            dailyReports: false,
          }),
        }
      )
      
      // Carica dati utente
      await useAuth.getState().checkAuth()
    } catch (error) {
      console.error('Registration error:', error)
      set({ 
        error: (error as Error).message || 'Errore durante la registrazione', 
        isLoading: false 
      })
      throw error
    }
  },

  checkAuth: async () => {
    try {
      set({ isLoading: true })
      
      const accountData = await account.get()
      const prefs = await account.getPrefs()
      const userTeams = await teams.list()
      
      let role: User['role'] = 'user'
      if (userTeams.teams.some(t => t.$id === 'super-admins')) {
        role = 'super_admin'
      } else if (userTeams.teams.some(t => t.$id === 'admins')) {
        role = 'admin'
      }
      
      const user: User = {
        id: accountData.$id,
        email: accountData.email,
        name: accountData.name,
        role,
        avatar: prefs.avatar,
        phone: prefs.phone,
        notificationPreferences: prefs.notificationPreferences || {
          email: true,
          sms: false,
          securityAlerts: true,
          dailyReports: false,
        },
        createdAt: new Date(accountData.$createdAt),
        updatedAt: new Date(accountData.$updatedAt),
      }
      
      set({ user, isAuthenticated: true, isLoading: false })
    } catch (error) {
      set({ user: null, isAuthenticated: false, isLoading: false })
    }
  },

  updateUser: (userData: Partial<User>) => {
    set(state => ({
      user: state.user ? { ...state.user, ...userData } : null
    }))
  },
}))

// Inizializza auth check all'avvio
if (typeof window !== 'undefined') {
  useAuth.getState().checkAuth()
}
