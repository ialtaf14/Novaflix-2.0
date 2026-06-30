import { io } from 'socket.io-client'
import { useAuthStore } from '../store/useAuthStore'

let socket = null

// In production, connect to the Render backend; in dev, use local proxy
const SOCKET_URL = import.meta.env.PROD
  ? (import.meta.env.VITE_API_URL?.replace('/api', '') || 'https://novaflix-backend.onrender.com')
  : ''

export function getSocket() {
  if (!socket) {
    const username = useAuthStore.getState().user?.username || 'anonymous'
    socket = io(SOCKET_URL, { path: '/ws/socket.io', auth: { username }, transports: ['websocket', 'polling'] })
    socket.on('connect', () => console.log('[Socket.IO] Connected:', socket.id))
    socket.on('disconnect', () => console.log('[Socket.IO] Disconnected'))
  }
  return socket
}

export function disconnectSocket() {
  if (socket) {
    socket.disconnect()
    socket = null
  }
}
