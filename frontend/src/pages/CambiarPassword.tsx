import { useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "motion/react";
import { useAuth } from "../auth/useAuth";
import { api, errorMessage } from "../lib/api";
import { GlassInput, GlassButton, ErrorAlert, SuccessAlert, InfoAlert } from "../components/ui";

export default function CambiarPassword() {
  const { user, setPrimerLoginFalse, logout } = useAuth();
  const navigate = useNavigate();

  const [oldPwd, setOldPwd]       = useState("");
  const [newPwd, setNewPwd]       = useState("");
  const [confirmPwd, setConfirmPwd] = useState("");
  const [error, setError]         = useState<string | null>(null);
  const [loading, setLoading]     = useState(false);
  const [ok, setOk]               = useState(false);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    if (newPwd.length < 8) {
      setError("La nueva contraseña debe tener al menos 8 caracteres");
      return;
    }
    if (newPwd !== confirmPwd) {
      setError("Las contraseñas no coinciden");
      return;
    }
    setLoading(true);
    try {
      await api.post("/auth/change-password", { old_password: oldPwd, new_password: newPwd });
      setPrimerLoginFalse();
      setOk(true);
      setTimeout(() => navigate("/"), 1200);
    } catch (err) {
      setError(errorMessage(err, "No se pudo cambiar la contraseña"));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="max-w-md mx-auto">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, ease: "easeOut" }}
      >
        <header className="mb-6">
          <div className="inline-flex w-12 h-12 rounded-xl bg-brand-600 text-white items-center justify-center font-bold text-xl mb-3 shadow-lg shadow-brand-600/40">
            🔑
          </div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Cambiar contraseña</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
            {user?.primer_login ? "Establece tu contraseña antes de continuar." : "Actualiza tu contraseña de acceso."}
          </p>
        </header>

        {user?.primer_login && (
          <div className="mb-4">
            <InfoAlert message="Es tu primer ingreso. Debes definir una contraseña nueva antes de continuar." />
          </div>
        )}

        <motion.form
          onSubmit={onSubmit}
          noValidate
          className="bg-white dark:bg-white/5 backdrop-blur-xl border border-slate-200 dark:border-white/10 rounded-2xl shadow-xl dark:shadow-black/40 p-6 space-y-4"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.15, duration: 0.4 }}
        >
          <GlassInput
            id="old-password"
            label="Contraseña actual"
            type="password"
            autoComplete="current-password"
            required
            value={oldPwd}
            onChange={(e) => setOldPwd(e.target.value)}
          />

          <GlassInput
            id="new-password"
            label="Nueva contraseña"
            type="password"
            autoComplete="new-password"
            minLength={8}
            required
            value={newPwd}
            onChange={(e) => setNewPwd(e.target.value)}
            hint="Mínimo 8 caracteres"
          />

          <GlassInput
            id="confirm-password"
            label="Confirmar nueva contraseña"
            type="password"
            autoComplete="new-password"
            minLength={8}
            required
            value={confirmPwd}
            onChange={(e) => setConfirmPwd(e.target.value)}
          />

          {error && <ErrorAlert message={error} />}
          {ok && <SuccessAlert message="Contraseña actualizada. Redirigiendo…" />}

          <div className="flex gap-3 pt-1">
            <GlassButton type="submit" disabled={loading} className="flex-1">
              {loading ? "Guardando…" : "Cambiar contraseña"}
            </GlassButton>

            {!user?.primer_login && (
              <GlassButton type="button" variant="secondary" onClick={() => navigate(-1)}>
                Cancelar
              </GlassButton>
            )}

            {user?.primer_login && (
              <GlassButton
                type="button"
                variant="secondary"
                onClick={() => { logout(); navigate("/login"); }}
              >
                Salir
              </GlassButton>
            )}
          </div>
        </motion.form>
      </motion.div>
    </div>
  );
}
