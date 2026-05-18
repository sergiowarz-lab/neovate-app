import { useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../auth/useAuth";
import { api, errorMessage } from "../lib/api";

export default function CambiarPassword() {
  const { user, setPrimerLoginFalse, logout } = useAuth();
  const navigate = useNavigate();

  const [oldPwd, setOldPwd] = useState("");
  const [newPwd, setNewPwd] = useState("");
  const [confirmPwd, setConfirmPwd] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [ok, setOk] = useState(false);

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
      <h1 className="text-2xl font-bold mb-2">Cambiar contraseña</h1>
      {user?.primer_login && (
        <p className="text-sm text-amber-700 dark:text-amber-300 bg-amber-50 dark:bg-amber-950 border border-amber-200 dark:border-amber-800 rounded-md px-3 py-2 mb-4" role="status">
          Es tu primer ingreso. Debes definir una contraseña nueva antes de continuar.
        </p>
      )}

      <form
        onSubmit={onSubmit}
        className="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg shadow-sm p-6 space-y-4"
        noValidate
      >
        <div>
          <label htmlFor="old-password" className="block text-sm font-medium text-slate-700 dark:text-slate-300">
            Contraseña actual
          </label>
          <input
            id="old-password"
            type="password"
            autoComplete="current-password"
            required
            value={oldPwd}
            onChange={(e) => setOldPwd(e.target.value)}
            className="mt-1 w-full px-3 py-2 rounded-md border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-900"
          />
        </div>

        <div>
          <label htmlFor="new-password" className="block text-sm font-medium text-slate-700 dark:text-slate-300">
            Nueva contraseña <span className="text-xs text-slate-500">(mínimo 8 caracteres)</span>
          </label>
          <input
            id="new-password"
            type="password"
            autoComplete="new-password"
            minLength={8}
            required
            value={newPwd}
            onChange={(e) => setNewPwd(e.target.value)}
            className="mt-1 w-full px-3 py-2 rounded-md border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-900"
          />
        </div>

        <div>
          <label htmlFor="confirm-password" className="block text-sm font-medium text-slate-700 dark:text-slate-300">
            Confirmar nueva contraseña
          </label>
          <input
            id="confirm-password"
            type="password"
            autoComplete="new-password"
            minLength={8}
            required
            value={confirmPwd}
            onChange={(e) => setConfirmPwd(e.target.value)}
            className="mt-1 w-full px-3 py-2 rounded-md border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-900"
          />
        </div>

        {error && (
          <p className="text-sm text-rose-700 dark:text-rose-300 bg-rose-50 dark:bg-rose-950 border border-rose-200 dark:border-rose-800 rounded-md px-3 py-2" role="alert">
            {error}
          </p>
        )}
        {ok && (
          <p className="text-sm text-emerald-700 dark:text-emerald-300 bg-emerald-50 dark:bg-emerald-950 border border-emerald-200 dark:border-emerald-800 rounded-md px-3 py-2" role="status">
            Contraseña actualizada. Redirigiendo…
          </p>
        )}

        <div className="flex gap-2">
          <button
            type="submit"
            disabled={loading}
            className="flex-1 py-2.5 rounded-md bg-brand-600 hover:bg-brand-700 text-white font-medium disabled:opacity-60"
          >
            {loading ? "Guardando…" : "Cambiar contraseña"}
          </button>
          {!user?.primer_login && (
            <button
              type="button"
              onClick={() => navigate(-1)}
              className="px-4 py-2.5 rounded-md border border-slate-300 dark:border-slate-600 text-slate-700 dark:text-slate-300"
            >
              Cancelar
            </button>
          )}
          {user?.primer_login && (
            <button
              type="button"
              onClick={() => { logout(); navigate("/login"); }}
              className="px-4 py-2.5 rounded-md border border-slate-300 dark:border-slate-600 text-slate-700 dark:text-slate-300"
            >
              Salir
            </button>
          )}
        </div>
      </form>
    </div>
  );
}
