import { useEffect, useState } from 'react'
import { X, CheckCircle, AlertCircle, Info, AlertTriangle } from 'lucide-react'
import { Toast, toastStore } from '@/lib/toast'

interface ToasterProps {
  toasts?: Toast[]
}

export function Toaster({ toasts: externalToasts }: ToasterProps) {
  const [toasts, setToasts] = useState<Toast[]>([])

  useEffect(() => {
    if (externalToasts) {
      setToasts(externalToasts)
      return
    } else {
      const unsubscribe = toastStore.subscribe(setToasts)
      return () => {
        unsubscribe()
      }
    }
  }, [externalToasts])

  const getIcon = (type?: Toast['type']) => {
    switch (type) {
      case 'success':
        return <CheckCircle className="h-5 w-5 text-green-400" />
      case 'error':
        return <AlertCircle className="h-5 w-5 text-red-400" />
      case 'warning':
        return <AlertTriangle className="h-5 w-5 text-yellow-400" />
      case 'info':
        return <Info className="h-5 w-5 text-blue-400" />
      default:
        return <Info className="h-5 w-5 text-gray-400" />
    }
  }

  const getStyles = (type?: Toast['type']) => {
    switch (type) {
      case 'success':
        return 'bg-green-500/20 border-green-500/50'
      case 'error':
        return 'bg-red-500/20 border-red-500/50'
      case 'warning':
        return 'bg-yellow-500/20 border-yellow-500/50'
      case 'info':
        return 'bg-blue-500/20 border-blue-500/50'
      default:
        return 'bg-dark-surface border-dark-border'
    }
  }

  return (
    <div className="fixed bottom-4 right-4 z-50 flex flex-col gap-2">
      {toasts.map((toast) => (
        <div
          key={toast.id}
          className={`flex items-start gap-3 min-w-[300px] max-w-md p-4 rounded-lg border backdrop-blur-sm animate-slide-in ${getStyles(toast.type)}`}
        >
          {getIcon(toast.type)}
          <div className="flex-1">
            <p className="font-medium text-sm">{toast.title}</p>
            {toast.description && (
              <p className="text-xs text-gray-400 mt-1">{toast.description}</p>
            )}
          </div>
          <button
            onClick={() => toastStore.removeToast(toast.id)}
            className="text-gray-400 hover:text-white"
          >
            <X className="h-4 w-4" />
          </button>
        </div>
      ))}
    </div>
  )
}