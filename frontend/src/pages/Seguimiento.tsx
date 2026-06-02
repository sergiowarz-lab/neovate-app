import { useEffect, useState } from "react";
import { motion } from "motion/react";
import { api, errorMessage } from "../lib/api";
import type { EstadoSeguimiento, SeguimientoMensual } from "../types";
import {
  PageHeader, GlassInput, GlassSelect, TableWrapper, TableHead,
  Th, Td, StatusBadge, ErrorAlert, LoadingRow, EmptyRow,
} from "../components/ui";

const MESES = ["", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
               "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"];

const STATUS_VARIANT: Record<EstadoSeguimiento, "success" | "warning" | "danger"> = {
  Cumple:   "success",
  En_mora:  "danger",
  Pendiente: "warning",
};

const STATUS_LABEL: Record<EstadoSeguimiento, string> = {
  Cumple:   "Cumple",
  En_mora:  "En mora",
  Pendiente: "Pendiente",
};

export default function Seguimiento() {
  const hoy = new Date();
  const [anio, setAnio] = useState<number>(hoy.getFullYear());
  const [mes, setMes] = useState<number>(hoy.getMonth() + 1);
  const [rows, setRows] = useState<SeguimientoMensual[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    api.get<SeguimientoMensual[]>("/seguimiento", { params: { anio, mes } })
      .then((r) => setRows(r.data))
      .catch((e) => setError(errorMessage(e, "Error cargando seguimiento")))
      .finally(() => setLoading(false));
  }, [anio, mes]);

  const counts = rows.reduce(
    (acc, r) => {
      if (r.ss_estado) acc[r.ss_estado] = (acc[r.ss_estado] ?? 0) + 1;
      return acc;
    },
    {} as Partial<Record<EstadoSeguimiento, number>>
  );

  return (
    <div>
      <PageHeader
        title="Seguimiento mensual"
        subtitle={`Estado de pago SS y Nómina · ${MESES[mes]} ${anio}`}
      />

      <motion.fieldset
        className="mb-5 flex flex-wrap items-end gap-3"
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3, delay: 0.1 }}
      >
        <legend className="sr-only">Filtros de período</legend>
        <div className="w-28">
          <GlassInput
            id="anio"
            label="Año"
            type="number"
            value={anio}
            min={2020}
            max={2100}
            onChange={(e) => setAnio(Number(e.target.value))}
          />
        </div>
        <div className="w-40">
          <GlassSelect
            id="mes"
            label="Mes"
            value={mes}
            onChange={(e) => setMes(Number(e.target.value))}
          >
            {Array.from({ length: 12 }, (_, i) => i + 1).map((m) => (
              <option key={m} value={m}>{MESES[m]}</option>
            ))}
          </GlassSelect>
        </div>
      </motion.fieldset>

      {!loading && rows.length > 0 && (
        <motion.div
          className="flex flex-wrap gap-3 mb-5"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.3, delay: 0.15 }}
        >
          {(["Cumple", "En_mora", "Pendiente"] as EstadoSeguimiento[]).map((s) => (
            counts[s] !== undefined && (
              <div key={s} className="flex items-center gap-2">
                <StatusBadge label={`${STATUS_LABEL[s]}: ${counts[s]}`} variant={STATUS_VARIANT[s]} />
              </div>
            )
          ))}
        </motion.div>
      )}

      {error && <div className="mb-4"><ErrorAlert message={error} /></div>}

      <TableWrapper>
        <table className="min-w-full">
          <caption className="sr-only">Seguimiento mensual</caption>
          <TableHead>
            <tr>
              <Th>Empresa</Th>
              <Th>SS</Th>
              <Th>Plazo SS</Th>
              <Th>Pago SS</Th>
              <Th>Días mora</Th>
              <Th>Nómina</Th>
            </tr>
          </TableHead>
          <tbody className="divide-y divide-slate-100 dark:divide-white/5">
            {loading && <LoadingRow cols={6} />}
            {!loading && rows.length === 0 && <EmptyRow cols={6} message="Sin registros para este período" />}
            {!loading && rows.map((s, i) => (
              <motion.tr
                key={`${s.nit9}-${s.anio}-${s.mes}`}
                className="hover:bg-slate-50/80 dark:hover:bg-white/5 transition-colors"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.2, delay: i * 0.02 }}
              >
                <Td>
                  <div className="font-medium text-slate-900 dark:text-white">{s.nombre_empresa ?? s.nit9}</div>
                  <div className="text-xs font-mono text-slate-400 dark:text-slate-500 mt-0.5">{s.nit9}</div>
                </Td>
                <Td>
                  {s.ss_estado && (
                    <StatusBadge
                      label={STATUS_LABEL[s.ss_estado]}
                      variant={STATUS_VARIANT[s.ss_estado]}
                      pulse={s.ss_estado === "Pendiente"}
                    />
                  )}
                </Td>
                <Td className="text-sm tabular-nums text-slate-600 dark:text-slate-400">{s.ss_fecha_plazo ?? "—"}</Td>
                <Td className="text-sm tabular-nums text-slate-600 dark:text-slate-400">{s.ss_fecha_pago ?? "—"}</Td>
                <Td className="text-sm tabular-nums text-right font-medium">
                  {s.ss_dias_mora != null ? (
                    <span className={s.ss_dias_mora > 0 ? "text-rose-600 dark:text-rose-400" : "text-slate-500"}>
                      {s.ss_dias_mora}
                    </span>
                  ) : "—"}
                </Td>
                <Td>
                  {s.nomina_estado && (
                    <StatusBadge
                      label={STATUS_LABEL[s.nomina_estado]}
                      variant={STATUS_VARIANT[s.nomina_estado]}
                      pulse={s.nomina_estado === "Pendiente"}
                    />
                  )}
                </Td>
              </motion.tr>
            ))}
          </tbody>
        </table>
      </TableWrapper>
    </div>
  );
}
