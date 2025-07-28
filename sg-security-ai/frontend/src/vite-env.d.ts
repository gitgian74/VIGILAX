/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_VIAM_API_KEY: string
  readonly VITE_VIAM_API_KEY_ID: string
  readonly VITE_VIAM_ROBOT_ADDRESS: string
  readonly VITE_APPWRITE_ENDPOINT: string
  readonly VITE_APPWRITE_PROJECT_ID: string
  readonly VITE_APPWRITE_DATABASE_ID: string
  readonly VITE_APPWRITE_API_KEY: string
  readonly VITE_APP_NAME: string
  readonly VITE_APP_VERSION: string
  readonly VITE_APP_ENV: string
  readonly VITE_VIDEO_BUFFER_MINUTES: string
  readonly VITE_LOITERING_THRESHOLD_SECONDS: string
  readonly VITE_ML_CONFIDENCE_THRESHOLD: string
  readonly VITE_LOCAL_RECORDINGS_PATH: string
  readonly VITE_VIDEO_RECORDING_PATH: string
  readonly VITE_WEBCAM_RECORDING_PATH: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}