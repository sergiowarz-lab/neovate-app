/**
 * CamaraCaptura — captura una foto con la cámara del celular y extrae texto
 * usando Tesseract.js (OCR en el cliente, sin necesidad de servidor).
 *
 * Solo se muestra en dispositivos móviles (detectado en el padre SubirPlanilla).
 * Instalar: npm install tesseract.js
 */
import { useRef, useState } from "react";

interface Props {
  onTextoExtraido: (texto: string) => void;
  procesando: boolean;
}

export default function CamaraCaptura({ onTextoExtraido, procesando }: Props) {
  const inputRef = useRef<HTMLInputElement>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [leyendo, setLeyendo] = useState(false);
  const [progreso, setProgreso] = useState(0);

  async function handleImagen(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;

    const url = URL.createObjectURL(file);
    setPreview(url);
    setLeyendo(true);
    setProgreso(0);

    try {
      // Importación dinámica — Tesseract.js solo carga si se usa esta función
      const Tesseract = await import("tesseract.js");
      const { data } = await Tesseract.recognize(file, "spa", {
        logger: (m) => {
          if (m.status === "recognizing text") {
            setProgreso(Math.round((m.progress ?? 0) * 100));
          }
        },
      });
      onTextoExtraido(data.text);
    } catch {
      onTextoExtraido("");
    } finally {
      setLeyendo(false);
    }
  }

  return (
    <div className="space-y-3">
      <label className="block text-xs font-medium text-slate-500 mb-1">
        Foto del comprobante
      </label>

      {/* Botón de cámara */}
      <button
        type="button"
        onClick={() => inputRef.current?.click()}
        disabled={leyendo || procesando}
        className="w-full py-8 rounded-xl border-2 border-dashed border-brand-400/40
                   flex flex-col items-center gap-2 text-brand-500 dark:text-brand-400
                   hover:border-brand-400 hover:bg-brand-500/5 transition-all
                   disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <span className="text-3xl">📷</span>
        <span className="text-sm font-medium">Tomar foto o elegir imagen</span>
        <span className="text-xs text-slate-400">JPG, PNG, HEIC</span>
      </button>

      {/* Input oculto — capture="environment" abre cámara trasera en móvil */}
      <input
        ref={inputRef}
        type="file"
        accept="image/*"
        capture="environment"
        className="hidden"
        onChange={handleImagen}
      />

      {/* Preview de la imagen */}
      {preview && (
        <div className="relative rounded-xl overflow-hidden border border-slate-200 dark:border-white/10">
          <img src={preview} alt="Previsualización" className="w-full max-h-48 object-contain bg-black/5" />
          {leyendo && (
            <div className="absolute inset-0 flex flex-col items-center justify-center bg-black/50 text-white">
              <div className="w-32 h-1.5 bg-white/20 rounded-full overflow-hidden mb-2">
                <div
                  className="h-full bg-brand-400 rounded-full transition-all duration-300"
                  style={{ width: `${progreso}%` }}
                />
              </div>
              <span className="text-xs">Extrayendo texto… {progreso}%</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
