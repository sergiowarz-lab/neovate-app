import { Link } from "react-router-dom";
import { motion } from "motion/react";

export default function NotFound() {
  return (
    <div className="min-h-[65vh] flex flex-col items-center justify-center text-center px-4">

      <motion.div
        initial={{ scale: 0.5, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ type: "spring", stiffness: 160, damping: 16 }}
        style={{ perspective: "800px" }}
        className="relative mb-6"
      >
        {/* Background glow */}
        <div className="absolute inset-0 blur-3xl opacity-25 bg-brand-500 scale-75 rounded-full" />

        <span
          className="relative select-none text-[9rem] sm:text-[12rem] font-bold font-mono leading-none text-brand-500 dark:text-brand-400"
          style={{ filter: "drop-shadow(0 0 40px rgba(34,197,94,0.8)) drop-shadow(0 0 80px rgba(34,197,94,0.4))" }}
        >
          404
        </span>
      </motion.div>

      {/* Pulsing rings */}
      <motion.div
        className="absolute w-56 h-56 rounded-full border border-brand-500/20"
        animate={{ scale: [1, 1.4, 1], opacity: [0.5, 0, 0.5] }}
        transition={{ repeat: Infinity, duration: 3, ease: "easeInOut" }}
      />
      <motion.div
        className="absolute w-72 h-72 rounded-full border border-brand-500/10"
        animate={{ scale: [1, 1.3, 1], opacity: [0.3, 0, 0.3] }}
        transition={{ repeat: Infinity, duration: 3, ease: "easeInOut", delay: 0.4 }}
      />

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, delay: 0.25 }}
      >
        <p className="text-xs font-mono text-brand-600 dark:text-brand-700 tracking-widest mb-2">ERROR_CODE :: 404</p>
        <h1 className="text-2xl font-bold font-mono text-slate-900 dark:text-brand-400">PÁGINA NO ENCONTRADA</h1>
        <p className="mt-2 text-slate-500 dark:text-brand-700 font-mono text-sm max-w-xs mx-auto">
          // La ruta solicitada no existe en el sistema.
        </p>

        <Link
          to="/"
          className="
            mt-8 inline-flex items-center gap-2 px-6 py-3 rounded-xl
            font-bold font-mono tracking-widest text-sm
            bg-brand-500 dark:bg-black text-black dark:text-brand-400
            border-2 border-transparent dark:border-brand-500/50
            hover:bg-brand-400 dark:hover:bg-brand-500/10
            dark:hover:shadow-[0_0_30px_rgba(34,197,94,0.4)]
            transition-all duration-300
          "
        >
          ← VOLVER AL DASHBOARD
        </Link>
      </motion.div>
    </div>
  );
}
