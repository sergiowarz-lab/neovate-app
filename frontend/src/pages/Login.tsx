import { useState, type FormEvent } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { motion } from "motion/react";
import { useAuth } from "../auth/useAuth";
import { errorMessage } from "../lib/api";
import { use3DTilt } from "../hooks/use3DTilt";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const from = (location.state as { from?: { pathname?: string } })?.from?.pathname ?? "/";

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const tilt = use3DTilt(7);

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
    <div className="min-h-full grid place-items-center px-4 py-12 bg-[#f1f0f7] dark:bg-[#0f0e17]">
      <div className="fixed inset-0 pointer-events-none overflow-hidden z-0" aria-hidden="true">
        <div className="orb-a absolute top-[-20%] left-[-10%] w-[600px] h-[600px] rounded-full bg-brand-400/8 dark:bg-brand-500/8 blur-[130px]" />
        <div className="orb-b absolute bottom-[-15%] right-[-5%] w-[500px] h-[500px] rounded-full bg-brand-600/5 dark:bg-brand-600/6 blur-[110px]" />
      </div>

      <motion.main
        id="main-content"
        className="relative z-10 w-full max-w-sm"
        initial={{ opacity: 0, y: 28 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: "easeOut" }}
      >
        <header className="mb-7 text-center">
          <motion.div
            className="inline-flex w-14 h-14 rounded-2xl items-center justify-center font-bold text-xl mb-4
                       bg-brand-500 text-black
                       shadow-2xl shadow-brand-500/30"
            initial={{ scale: 0, rotate: -20 }}
            animate={{ scale: 1, rotate: 0 }}
            transition={{ delay: 0.15, type: "spring", stiffness: 220, damping: 14 }}
            style={{ filter: "drop-shadow(0 0 20px rgba(201,168,76,0.5))" }}
          >
            N
          </motion.div>
          <h1 className="text-xl font-bold text-slate-900 dark:text-[#e8e6f0]">Sistema Neovate</h1>
          <p className="text-sm text-slate-500 dark:text-slate-500 mt-1">Validación y Seguimiento de Pagos SS</p>
        </header>

        <div style={{ perspective: "900px" }}>
          <div className="group/card relative">
            <div className="absolute -inset-px rounded-2xl opacity-0 group-hover/card:opacity-100 transition-opacity duration-500 holo-border" />
            <div ref={tilt.ref} style={tilt.style} onMouseMove={tilt.onMouseMove} onMouseLeave={tilt.onMouseLeave}>
              <motion.form
                onSubmit={onSubmit}
                noValidate
                className="relative bg-white dark:bg-[#1a1825] border border-slate-200/80 dark:border-white/[0.07] rounded-2xl shadow-xl dark:shadow-black/60 p-7 space-y-4"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.25, duration: 0.4 }}
              >
                <div className="absolute top-0 left-0 right-0 h-[2px] rounded-t-2xl bg-gradient-to-r from-transparent via-brand-400 to-transparent" />

                <div>
                  <label htmlFor="username" className="block text-xs font-semibold uppercase tracking-widest text-slate-500 dark:text-slate-500 mb-1.5">
                    Usuario
                  </label>
                  <input
                    id="username" name="username" type="text" autoComplete="username" required
                    value={username} onChange={(e) => setUsername(e.target.value)}
                    className="w-full px-4 py-2.5 rounded-xl border border-slate-200 dark:border-white/[0.08] bg-slate-50 dark:bg-black/40 text-slate-900 dark:text-[#e8e6f0] placeholder:text-slate-300 dark:placeholder:text-slate-700 focus:border-brand-500 focus:ring-2 focus:ring-brand-500/25 transition-all duration-200"
                    aria-required="true"
                  />
                </div>

                <div>
                  <label htmlFor="password" className="block text-xs font-semibold uppercase tracking-widest text-slate-500 dark:text-slate-500 mb-1.5">
                    Contraseña
                  </label>
                  <input
                    id="password" name="password" type="password" autoComplete="current-password" required
                    value={password} onChange={(e) => setPassword(e.target.value)}
                    className="w-full px-4 py-2.5 rounded-xl border border-slate-200 dark:border-white/[0.08] bg-slate-50 dark:bg-black/40 text-slate-900 dark:text-[#e8e6f0] placeholder:text-slate-300 dark:placeholder:text-slate-700 focus:border-brand-500 focus:ring-2 focus:ring-brand-500/25 transition-all duration-200"
                    aria-required="true"
                  />
                </div>

                {error && (
                  <motion.p
                    role="alert" aria-live="assertive"
                    className="text-sm text-rose-700 dark:text-rose-400 bg-rose-50 dark:bg-rose-500/8 border border-rose-200 dark:border-rose-500/20 rounded-xl px-4 py-2.5"
                    initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }}
                  >
                    {error}
                  </motion.p>
                )}

                <button
                  type="submit" disabled={loading}
                  className="w-full py-2.5 rounded-xl font-semibold text-sm text-black bg-brand-500 hover:bg-brand-400 active:bg-brand-600 shadow-lg shadow-brand-500/25 hover:shadow-[0_0_24px_rgba(201,168,76,0.4)] disabled:opacity-60 disabled:cursor-not-allowed transition-all duration-200 cursor-pointer"
                >
                  {loading ? "Ingresando…" : "Ingresar"}
                </button>

                <p className="text-xs text-center text-slate-400 dark:text-slate-600">
                  ¿Olvidaste tu contraseña? Contacta a un administrador.
                </p>
              </motion.form>
            </div>
          </div>
        </div>
      </motion.main>
    </div>
  );
}
