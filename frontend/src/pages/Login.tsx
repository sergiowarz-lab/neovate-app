import { useState, type FormEvent } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { useAuth } from "../auth/useAuth";
import { errorMessage } from "../lib/api";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const from = (location.state as { from?: { pathname?: string } })?.from?.pathname ?? "/";

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const res = await login(username, password);
      navigate(res.primer_login ? "/cambiar-password" : from, { replace: true });
    } catch (err) {
      setError(errorMessage(err, "No se pudo iniciar sesión"));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-full grid place-items-center px-4 py-12 bg-slate-50 dark:bg-slate-900">
      <main id="main-content" className="w-full max-w-md">
        <header className="mb-6 text-center">
          <span className="inline-block w-12 h-12 rounded-lg bg-brand-600 text-white grid place-items-center font-bold text-2xl mb-3">N</span>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-slate-100">Sistema Neovate</h1>
          <p className="text-sm text-slate-600 dark:text-slate-400 mt-1">Validación y Seguimiento de Pagos SS</p>
        </header>

        <form
          onSubmit={onSubmit}
          className="bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg shadow-sm p-6 space-y-4"
          noValidate
        >
          <div>
            <label htmlFor="username" className="block text-sm font-medium text-slate-700 dark:text-slate-300">
              Usuario
            </label>
            <input
              id="username"
              name="username"
              type="text"
              autoComplete="username"
              required
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="mt-1 w-full px-3 py-2 rounded-md border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-900 text-slate-900 dark:text-slate-100 focus:border-brand-500 focus:ring-2 focus:ring-brand-500/30"
              aria-required="true"
            />
          </div>

          <div>
            <label htmlFor="password" className="block text-sm font-medium text-slate-700 dark:text-slate-300">
              Contraseña
            </label>
            <input
              id="password"
              name="password"
              type="password"
              autoComplete="current-password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="mt-1 w-full px-3 py-2 rounded-md border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-900 text-slate-900 dark:text-slate-100 focus:border-brand-500 focus:ring-2 focus:ring-brand-500/30"
              aria-required="true"
            />
          </div>

          {error && (
            <p className="text-sm text-rose-700 dark:text-rose-300 bg-rose-50 dark:bg-rose-950 border border-rose-200 dark:border-rose-800 rounded-md px-3 py-2" role="alert" aria-live="assertive">
              {error}
            </p>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 rounded-md bg-brand-600 hover:bg-brand-700 text-white font-medium disabled:opacity-60 disabled:cursor-not-allowed"
          >
            {loading ? "Ingresando…" : "Ingresar"}
          </button>

          <p className="text-xs text-center text-slate-500 dark:text-slate-400">
            ¿Olvidaste tu contraseña? Contacta a un administrador.
          </p>
        </form>
      </main>
    </div>
  );
}
