/**
 * Tests del componente SubirPlanilla.
 *
 * Verifica el comportamiento del formulario de carga de PDFs:
 *   - renderizado inicial correcto
 *   - validaciones del formulario
 *   - flujo de carga exitoso
 *   - manejo de errores del servidor
 *
 * Para correr:
 *   npm run test
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'

import SubirPlanilla from '../pages/SubirPlanilla'
import { api } from '../lib/api'

// Mock del módulo api para no hacer llamadas reales
vi.mock('../lib/api', () => ({
  api: {
    get: vi.fn(),
    post: vi.fn(),
  },
  errorMessage: (err: unknown, fallback: string) => fallback,
}))

// Mock de useAuth para simular usuario admin
vi.mock('../auth/useAuth', () => ({
  useAuth: () => ({ user: { rol: 'admin', nit_empresa: null } }),
}))

const mockApi = api as { get: ReturnType<typeof vi.fn>; post: ReturnType<typeof vi.fn> }

function renderSubirPlanilla() {
  return render(
    <MemoryRouter>
      <SubirPlanilla />
    </MemoryRouter>
  )
}

describe('SubirPlanilla', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    // Por defecto, el endpoint de operadores devuelve lista estándar
    mockApi.get.mockResolvedValue({ data: ['ASOPAGOS', 'APORTES EN LINEA', 'NOMINA'] })
  })

  // ── Renderizado ─────────────────────────────────────────────────────────────

  it('muestra el título "Subir Planilla"', async () => {
    renderSubirPlanilla()
    expect(screen.getByText('Subir Planilla')).toBeInTheDocument()
  })

  it('carga la lista de operadores al montar', async () => {
    renderSubirPlanilla()
    await waitFor(() => {
      expect(mockApi.get).toHaveBeenCalledWith('/planillas/operadores')
    })
  })

  it('muestra ASOPAGOS en el select de operadores', async () => {
    renderSubirPlanilla()
    await waitFor(() => {
      expect(screen.getByText('ASOPAGOS')).toBeInTheDocument()
    })
  })

  it('botón "Subir y Validar" está presente', () => {
    renderSubirPlanilla()
    expect(screen.getByRole('button', { name: /subir y validar/i })).toBeInTheDocument()
  })

  // ── Validación del formulario ───────────────────────────────────────────────

  it('muestra error si se envía sin seleccionar archivo', async () => {
    renderSubirPlanilla()
    const boton = screen.getByRole('button', { name: /subir y validar/i })
    await userEvent.click(boton)
    expect(screen.getByText(/seleccionar un archivo pdf/i)).toBeInTheDocument()
  })

  // ── Flujo exitoso ───────────────────────────────────────────────────────────

  it('muestra spinner "Procesando…" tras un upload exitoso', async () => {
    mockApi.post.mockResolvedValueOnce({
      data: { reporte_id: 'ABC12345', hoja_destino: 'SS' },
    })
    mockApi.get
      .mockResolvedValueOnce({ data: ['ASOPAGOS'] }) // operadores
      .mockResolvedValue({ data: { estado: 'Procesando', rechazo: null } }) // polling

    renderSubirPlanilla()

    // Seleccionar archivo
    const input = document.querySelector('input[type="file"]') as HTMLInputElement
    const archivo = new File(['%PDF-1.4'], 'planilla.pdf', { type: 'application/pdf' })
    await userEvent.upload(input, archivo)

    // Enviar
    const boton = screen.getByRole('button', { name: /subir y validar/i })
    await userEvent.click(boton)

    await waitFor(() => {
      expect(screen.getByText(/procesando/i)).toBeInTheDocument()
    })
  })

  it('muestra resultado "Validado correctamente" cuando el backend responde OK', async () => {
    mockApi.post.mockResolvedValueOnce({
      data: { reporte_id: 'OK12345', hoja_destino: 'SS' },
    })
    mockApi.get
      .mockResolvedValueOnce({ data: ['ASOPAGOS'] })
      .mockResolvedValue({ data: { estado: 'Validado_ok', rechazo: null } })

    renderSubirPlanilla()

    const input = document.querySelector('input[type="file"]') as HTMLInputElement
    const archivo = new File(['%PDF-1.4'], 'planilla.pdf', { type: 'application/pdf' })
    await userEvent.upload(input, archivo)
    await userEvent.click(screen.getByRole('button', { name: /subir y validar/i }))

    await waitFor(() => {
      expect(screen.getByText(/validado correctamente/i)).toBeInTheDocument()
    })
  })

  it('muestra resultado "Rechazado" con el motivo cuando el backend rechaza', async () => {
    mockApi.post.mockResolvedValueOnce({
      data: { reporte_id: 'RE12345', hoja_destino: 'SS' },
    })
    mockApi.get
      .mockResolvedValueOnce({ data: ['ASOPAGOS'] })
      .mockResolvedValue({
        data: { estado: 'Rechazado', rechazo: 'NIT no coincide con el del archivo' },
      })

    renderSubirPlanilla()

    const input = document.querySelector('input[type="file"]') as HTMLInputElement
    const archivo = new File(['%PDF-1.4'], 'planilla.pdf', { type: 'application/pdf' })
    await userEvent.upload(input, archivo)
    await userEvent.click(screen.getByRole('button', { name: /subir y validar/i }))

    await waitFor(() => {
      expect(screen.getByText(/rechazado/i)).toBeInTheDocument()
      expect(screen.getByText(/NIT no coincide/i)).toBeInTheDocument()
    })
  })

  // ── Manejo de errores ───────────────────────────────────────────────────────

  it('muestra error cuando el upload falla', async () => {
    mockApi.post.mockRejectedValueOnce(new Error('Server Error'))

    renderSubirPlanilla()

    const input = document.querySelector('input[type="file"]') as HTMLInputElement
    const archivo = new File(['%PDF-1.4'], 'planilla.pdf', { type: 'application/pdf' })
    await userEvent.upload(input, archivo)
    await userEvent.click(screen.getByRole('button', { name: /subir y validar/i }))

    await waitFor(() => {
      expect(screen.getByText(/error al subir/i)).toBeInTheDocument()
    })
  })
})
