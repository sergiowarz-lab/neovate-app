import { Link } from "react-router-dom";

export default function NotFound() {
  return (
    <div className="text-center py-16">
      <h1 className="text-4xl font-bold">404</h1>
      <p className="mt-2 text-slate-600 dark:text-slate-400">La página solicitada no existe.</p>
      <Link to="/" className="mt-4 inline-block text-brand-700 dark:text-brand-400 hover:underline">Volver al Dashboard</Link>
    </div>
  );
}
