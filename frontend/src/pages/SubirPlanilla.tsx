import { useEffect, useRef, useState } from "react";
import { motion, AnimatePresence } from "motion/react";
import { api, errorMessage } from "../lib/api";
import { useAuth } from "../auth/useAuth";
import type { UploadStatus } from "../types";
import { PageHeader, GlassInput, GlassSelect, ErrorAlert } from "../components/ui";
import CamaraCaptura from "../components/CamaraCaptura";

const MESES = [
  { value: "01", label: "Enero" }, { value: "02", label: "Febrero" },
  { value: "03", label: "Marzo" }, { value: "04", label: "Abril" },
  { value: "05", label: "Mayo" }, { value: "06", label: "Junio" },
  { value: "07", label: "Julio" }, { value: "08", label: "Agosto" },
  { value: "09", label: "Septiembre" }, { value: "10", label: "Octubre" },
  { value: "11", label: "Noviembre" }, { value: "12", label: "Diciembre" },
];

const ESTADO_CONFIG = {
  Procesando:          { color: "text-yellow-500", icon: "⏳", label: "Procesando…" },
  Validado_ok:         { color: "text-emerald-500", icon: "✅", label: "Validado correctamente" },
  Rechazado:           { color: "text-rose-500",    icon: "❌", label: "Rechazado" },
  Validado_individual: { color: "text-blue-500",    icon: "ℹ️",  label: "Validado individual" },
};

type Tab = "pdf" | "camara";

export default function SubirPlanilla() {
  const { user } = useAuth();
  const [tab, setTab] = useState<Tab>("pdf");

  // form
  const [nit, setNit] = useState(user?.nit_empresa ?? "");
  const [operador, setOperador] = useState("");
  const [mes, setMes] = useState(String(new Date().getMonth()).padStart(2, "0") || "01");
  const [anio, setAnio] = useState(String(new Date().getFullYear()));
  const [archivo, setArchivo] = useState<File | null>(null);
  const [operadores, setOperadores] = useState<string[]>([]);

  // estado de envío
  const [enviando, setEnviando] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [resultado, setResultado] = useState<UploadStatus | null>(null);
  const pollingRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const isMobile = /Mobi|Android|iPhone|iPad/i.test(navigator.userAgent);

  useEffect(() => {
    api.get<string[]>("/planillas/operadores").then((r) => setOperadores(r.data)).catch(() => {});
  }, []);

  useEffect(() => () => { if (pollingRef.current) clearInterval(pollingRef.current); }, []);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!archivo) return;
    setError(null);
    setResultado(null);
    setEnviando(true);

    const fd = new FormData();
    fd.append("archivo", archivo);
    fd.append("nit", nit);
    fd.append("operador", operador);
    fd.append("mes", mes);
    fd.append("anio", anio);

    try {
      const { data } = await api.post<{ reporte_id: string; hoja_destino: string }>("/planillas/upload", fd);
      iniciarPolling(data.reporte_id);
    } catch (err) {
      setError(errorMessage(err, "Error al subir el archivo"));
      setEnviando(false);
    }
  }

  async function handleOcrSubmit(textoOcr: string) {
    if (!textoOcr.trim()) { setError("No se pudo extraer texto de la imagen"); return; }
    setError(null);
    setResultado(null);
    setEnviando(true);

    const fd = new FormData();
    fd.append("nit", nit);
    fd.append("operador", operador);
    fd.append("mes", mes);
    fd.append("anio", anio);
    fd.append("texto_extraido", textoOcr);

    try {
      const { data } = await api.post<{ reporte_id: string }>("/planillas/upload-ocr", fd);
      iniciarPolling(data.reporte_id);
    } catch (err) {
      setError(errorMessage(err, "Error al procesar la imagen"));
      setEnviando(false);
    }
  }

  function iniciarPolling(reporteId: string) {
    let intentos = 0;
    pollingRef.current = setInterval(async () => {
      intentos++;
      try {
        const { data } = await api.get<UploadStatus>(`/planillas/status/${reporteId}`);
        if (data.estado !== "Procesando") {
          clearInterval(pollingRef.current!);
          setResultado(data);
          setEnviando(false);
        }
      } catch {
        // seguir intentando
      }
      if (intentos >= 30) {
        clearInterval(pollingRef.current!);
        setError("Tiempo de espera agotado. Revisa el historial más tarde.");
        setEnviando(false);
      }
    }, 2000);
  }

  function resetear() {
    setResultado(null);
    setArchivo(null);
    setError(null);
  }

  const nitReadonly = user?.rol === "empresa";

  return (
    <div className="max-w-lg mx-auto">
      <PageHeader title="Subir Planilla" subtitle="Carga y valida una planilla de Seguridad Social o Nómina" />

      {/* Tabs pdf / cámara (solo móvil) */}
      {isMobile && (
        <div role="tablist" className="inline-flex gap-1 p-1 rounded-xl bg-slate-100 dark:bg-white/5 border border-slate-200 dark:border-white/10 mb-5">
          {(["pdf", "camara"] as Tab[]).map((t) => (
            <button
              key={t}
              role="tab"
              aria-selected={tab === t}
              onClick={() => { setTab(t); resetear(); }}
              className={`px-4 py-1.5 rounded-lg text-sm font-medium transition-all ${
                tab === t
                  ? "bg-white dark:bg-[#1a1825] text-brand-600 dark:text-brand-400 shadow-sm"
                  : "text-slate-500 hover:text-slate-700 dark:hover:text-slate-300"
              }`}
            >
              {t === "pdf" ? "📄 PDF" : "📷 Foto"}
            </button>
          ))}
        </div>
      )}

      <motion.div
        className="rounded-2xl border border-slate-200/70 dark:border-white/[0.07] bg-white dark:bg-[#1a1825] p-6"
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
      >
        {/* Campos comunes del formulario */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-xs font-medium text-slate-500 mb-1">NIT Empresa</label>
            <GlassInput
              value={nit}
              onChange={(e) => setNit(e.target.value)}
              placeholder="Ej: 900123456"
              required
              readOnly={nitReadonly}
              className={nitReadonly ? "opacity-70 cursor-not-allowed" : ""}
            />
          </div>

          <div>
            <label className="block text-xs font-medium text-slate-500 mb-1">Operador</label>
            <GlassSelect value={operador} onChange={(e) => setOperador(e.target.value)} required>
              <option value="">Selecciona un operador…</option>
              {operadores.map((op) => (
                <option key={op} value={op}>{op}</option>
              ))}
            </GlassSelect>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-slate-500 mb-1">Mes</label>
              <GlassSelect value={mes} onChange={(e) => setMes(e.target.value)} required>
                {MESES.map((m) => (
                  <option key={m.value} value={m.value}>{m.label}</option>
                ))}
              </GlassSelect>
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-500 mb-1">Año</label>
              <GlassInput
                type="number"
                value={anio}
                onChange={(e) => setAnio(e.target.value)}
                min={2020}
                max={2099}
                required
              />
            </div>
          </div>

          {/* Sección según tab */}
          {tab === "pdf" ? (
            <div>
              <label className="block text-xs font-medium text-slate-500 mb-1">Archivo PDF</label>
              <input
                type="file"
                accept=".pdf"
                onChange={(e) => setArchivo(e.target.files?.[0] ?? null)}
                required
                className="block w-full text-sm text-slate-600 dark:text-slate-400
                           file:mr-3 file:py-1.5 file:px-3 file:rounded-lg file:border-0
                           file:text-xs file:font-medium
                           file:bg-brand-500/10 file:text-brand-700 dark:file:text-brand-400
                           hover:file:bg-brand-500/20 cursor-pointer"
              />
            </div>
          ) : (
            <CamaraCaptura onTextoExtraido={handleOcrSubmit} procesando={enviando} />
          )}

          {error && <ErrorAlert message={error} />}

          {/* Resultado */}
          <AnimatePresence>
            {resultado && (
              <motion.div
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                className={`rounded-xl border p-4 ${
                  resultado.estado === "Validado_ok"
                    ? "border-emerald-300 bg-emerald-50 dark:border-emerald-700 dark:bg-emerald-900/20"
                    : "border-rose-300 bg-rose-50 dark:border-rose-700 dark:bg-rose-900/20"
                }`}
              >
                <div className={`text-sm font-semibold ${ESTADO_CONFIG[resultado.estado]?.color}`}>
                  {ESTADO_CONFIG[resultado.estado]?.icon} {ESTADO_CONFIG[resultado.estado]?.label}
                </div>
                {resultado.rechazo && (
                  <p className="mt-2 text-xs text-slate-600 dark:text-slate-400">{resultado.rechazo}</p>
                )}
                <button
                  type="button"
                  onClick={resetear}
                  className="mt-3 text-xs underline text-slate-500 hover:text-slate-700 dark:hover:text-slate-300"
                >
                  Subir otro archivo
                </button>
              </motion.div>
            )}
          </AnimatePresence>

          {tab === "pdf" && !resultado && (
            <button
              type="submit"
              disabled={enviando}
              className="w-full py-2.5 rounded-xl font-semibold text-sm transition-all
                         bg-brand-500 text-black hover:bg-brand-400
                         disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {enviando ? (
                <span className="flex items-center justify-center gap-2">
                  <span className="w-4 h-4 border-2 border-black/30 border-t-black rounded-full animate-spin" />
                  {resultado === null ? "Procesando…" : "Validando…"}
                </span>
              ) : "Subir y Validar"}
            </button>
          )}
        </form>
      </motion.div>
    </div>
  );
}
