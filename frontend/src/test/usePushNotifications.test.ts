/**
 * Tests del hook usePushNotifications.
 *
 * Verifica:
 *   - Detección de soporte del navegador
 *   - Flujo de suscripción (obtener clave VAPID → suscribirse → registrar en backend)
 *   - Flujo de desuscripción
 *   - Manejo de errores
 *
 * Para correr:
 *   npm test
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { usePushNotifications } from '../hooks/usePushNotifications'
import { api } from '../lib/api'

vi.mock('../lib/api', () => ({
  api: {
    get: vi.fn(),
    post: vi.fn(),
  },
}))

const mockApi = api as { get: ReturnType<typeof vi.fn>; post: ReturnType<typeof vi.fn> }

// ─── Mocks del navegador ────────────────────────────────────────────────────

const mockSubscription = {
  endpoint: 'https://fcm.googleapis.com/test',
  toJSON: () => ({
    endpoint: 'https://fcm.googleapis.com/test',
    keys: { p256dh: 'clave-p256dh', auth: 'clave-auth' },
  }),
  unsubscribe: vi.fn().mockResolvedValue(true),
}

const mockPushManager = {
  subscribe: vi.fn().mockResolvedValue(mockSubscription),
  getSubscription: vi.fn().mockResolvedValue(null),
}

const mockServiceWorkerRegistration = {
  pushManager: mockPushManager,
}

function mockearServiceWorker(suscritoInicial = false) {
  mockPushManager.getSubscription.mockResolvedValue(
    suscritoInicial ? mockSubscription : null
  )

  Object.defineProperty(navigator, 'serviceWorker', {
    value: {
      ready: Promise.resolve(mockServiceWorkerRegistration),
    },
    configurable: true,
    writable: true,
  })

  Object.defineProperty(window, 'PushManager', {
    value: {},
    configurable: true,
    writable: true,
  })
}


// ══════════════════════════════════════════════════════════════════════════════

describe('usePushNotifications', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    mockearServiceWorker()
    mockApi.get.mockResolvedValue({ data: { public_key: 'dmFwSWRQdWJsaWNLZXlFeGFtcGxl' } })
    mockApi.post.mockResolvedValue({ data: { mensaje: 'Suscripción registrada' } })
  })

  // ── Soporte del navegador ───────────────────────────────────────────────────

  it('detecta que el navegador soporta push cuando hay serviceWorker y PushManager', async () => {
    const { result } = renderHook(() => usePushNotifications())
    await act(async () => {})
    expect(result.current.soportado).toBe(true)
  })

  it('inicia con suscrito = false cuando no hay suscripción previa', async () => {
    const { result } = renderHook(() => usePushNotifications())
    await act(async () => {})
    expect(result.current.suscrito).toBe(false)
  })

  it('inicia con suscrito = true si ya había suscripción activa', async () => {
    mockearServiceWorker(true)
    const { result } = renderHook(() => usePushNotifications())
    await act(async () => {})
    expect(result.current.suscrito).toBe(true)
  })

  // ── Flujo de suscripción ───────────────────────────────────────────────────

  it('llama al backend para obtener la clave VAPID al suscribirse', async () => {
    const { result } = renderHook(() => usePushNotifications())
    await act(async () => { await result.current.suscribirse() })
    expect(mockApi.get).toHaveBeenCalledWith('/push/vapid-public-key')
  })

  it('registra la suscripción en el backend', async () => {
    const { result } = renderHook(() => usePushNotifications())
    await act(async () => { await result.current.suscribirse() })
    expect(mockApi.post).toHaveBeenCalledWith(
      '/push/subscribe',
      expect.objectContaining({ subscription: expect.any(Object) })
    )
  })

  it('marca suscrito = true tras suscripción exitosa', async () => {
    const { result } = renderHook(() => usePushNotifications())
    await act(async () => { await result.current.suscribirse() })
    expect(result.current.suscrito).toBe(true)
  })

  it('no hace nada si el navegador no soporta push', async () => {
    Object.defineProperty(window, 'PushManager', { value: undefined, configurable: true })
    const { result } = renderHook(() => usePushNotifications())
    await act(async () => { await result.current.suscribirse() })
    expect(mockApi.get).not.toHaveBeenCalled()
  })

  // ── Flujo de desuscripción ─────────────────────────────────────────────────

  it('llama al backend para eliminar la suscripción', async () => {
    mockearServiceWorker(true)
    const { result } = renderHook(() => usePushNotifications())
    await act(async () => { await result.current.desuscribirse() })
    expect(mockApi.post).toHaveBeenCalledWith(
      '/push/unsubscribe',
      expect.objectContaining({ subscription: expect.any(Object) })
    )
  })

  it('llama a subscription.unsubscribe() en el navegador', async () => {
    mockearServiceWorker(true)
    const { result } = renderHook(() => usePushNotifications())
    await act(async () => { await result.current.desuscribirse() })
    expect(mockSubscription.unsubscribe).toHaveBeenCalled()
  })

  it('marca suscrito = false tras desuscripción', async () => {
    mockearServiceWorker(true)
    const { result } = renderHook(() => usePushNotifications())
    await act(async () => { await result.current.desuscribirse() })
    expect(result.current.suscrito).toBe(false)
  })

  // ── Manejo de errores ──────────────────────────────────────────────────────

  it('no lanza excepción si el backend falla al suscribirse', async () => {
    mockApi.get.mockRejectedValueOnce(new Error('Network error'))
    const { result } = renderHook(() => usePushNotifications())
    await expect(act(async () => {
      await result.current.suscribirse()
    })).resolves.not.toThrow()
    expect(result.current.suscrito).toBe(false)
  })
})
