export type Rol = "admin" | "viewer" | "analista" | "empresa";

export type EstadoReporte = "Procesando" | "Validado_ok" | "Rechazado" | "Validado_individual";
export type EstadoSeguimiento = "Cumple" | "En_mora" | "Pendiente";
export type CoberturaFlag = "SI" | "NO" | "N/A";

export interface CurrentUser {
  username: string;
  nombre: string;
  email: string | null;
  rol: Rol;
  primer_login: boolean;
  nit_empresa: string | null;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in_minutes: number;
  primer_login: boolean;
  rol: Rol;
  nombre: string;
  nit_empresa: string | null;
}

export interface Empresa {
  nit: string;
  nit9: string;
  nombre_empresa: string;
  primer_mes: number | null;
  primer_anio: number | null;
  ultimo_mes: number | null;
  ultimo_anio: number | null;
  activa: boolean;
}

export interface DashboardKPIs {
  total_empresas: number;
  cumple: number;
  en_mora: number;
  pendiente: number;
  periodo_anio: number;
  periodo_mes: number;
}

export interface ReporteSS {
  id: string;
  nit: string;
  nit9: string;
  anio: number;
  mes_obligacion: number;
  operador: string | null;
  aliado: string | null;
  quien_envia: string | null;
  tipo_planilla: string | null;
  estado: EstadoReporte;
  fecha_pago: string | null;
  fecha_recepcion: string | null;
  cantidad_validos: number | null;
  rechazo: string | null;
}

export interface ReporteNomina {
  id: string;
  nit: string;
  nit9: string;
  aliado: string | null;
  anio: number;
  mes_obligacion: number;
  estado: EstadoReporte;
  fecha_pago: string | null;
  tipo_planilla: string | null;
  cantidad_validos: number | null;
  rechazo: string | null;
}

export interface SeguimientoMensual {
  nit9: string;
  anio: number;
  mes: number;
  mes_nombre: string | null;
  nombre_empresa: string | null;
  ss_fecha_plazo: string | null;
  ss_fecha_pago: string | null;
  ss_estado: EstadoSeguimiento | null;
  ss_dias_mora: number | null;
  ss_fecha_verif: string | null;
  nomina_fecha_plazo: string | null;
  nomina_fecha_pago: string | null;
  nomina_estado: EstadoSeguimiento | null;
  nomina_dias_mora: number | null;
  nomina_fecha_verif: string | null;
}

export interface Usuario {
  username: string;
  nombre: string;
  email: string | null;
  rol: Rol;
  nit_empresa: string | null;
  activo: boolean;
  primer_login: boolean;
  fecha_creacion: string;
  ultimo_acceso: string | null;
}

export interface UploadStatus {
  reporte_id: string;
  estado: EstadoReporte;
  hoja_destino: string;
  rechazo: string | null;
}
