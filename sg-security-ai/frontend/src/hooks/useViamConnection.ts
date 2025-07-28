import { useState, useEffect, useCallback } from 'react'
import { connectToRobot, disconnectFromRobot, getCamera, RobotClient, StreamClient } from '@/config/viam.config'
import { CameraClient } from '@viamrobotics/sdk'

interface ViamConnectionState {
  isConnected: boolean
  isConnecting: boolean
  error: string | null
  robotClient: RobotClient | null
  streamClient: StreamClient | null
}

export function useViamConnection() {
  const [state, setState] = useState<ViamConnectionState>({
    isConnected: false,
    isConnecting: false,
    error: null,
    robotClient: null,
    streamClient: null,
  })

  const connect = useCallback(async () => {
    setState(prev => ({ ...prev, isConnecting: true, error: null }))
    
    try {
      const client = await connectToRobot()
      const stream = new (await import('@viamrobotics/sdk')).StreamClient(client)
      
      setState({
        isConnected: true,
        isConnecting: false,
        error: null,
        robotClient: client,
        streamClient: stream,
      })
    } catch (error) {
      console.error('Errore connessione Viam:', error)
      setState({
        isConnected: false,
        isConnecting: false,
        error: (error as Error).message || 'Errore di connessione',
        robotClient: null,
        streamClient: null,
      })
    }
  }, [])

  const disconnect = useCallback(async () => {
    await disconnectFromRobot()
    setState({
      isConnected: false,
      isConnecting: false,
      error: null,
      robotClient: null,
      streamClient: null,
    })
  }, [])

  const getCameraClient = useCallback(async (cameraName: string): Promise<CameraClient | null> => {
    if (!state.isConnected) {
      await connect()
    }
    
    try {
      return await getCamera(cameraName)
    } catch (error) {
      console.error(`Errore accesso camera ${cameraName}:`, error)
      return null
    }
  }, [state.isConnected, connect])

  // Auto-connect all'avvio
  useEffect(() => {
    connect()
    
    // Cleanup alla disconnessione
    return () => {
      disconnect()
    }
  }, [connect, disconnect])

  // Riconnessione automatica in caso di errore
  useEffect(() => {
    if (state.error && !state.isConnecting) {
      const timeout = setTimeout(() => {
        console.log('Tentativo di riconnessione...')
        connect()
      }, 5000)
      
      return () => clearTimeout(timeout)
    }
  }, [state.error, state.isConnecting, connect])

  return {
    ...state,
    connect,
    disconnect,
    getCameraClient,
  }
}
