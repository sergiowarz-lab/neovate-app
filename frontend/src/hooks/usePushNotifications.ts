/**
 * Hook para gestionar suscripciones Web Push con VAPID.
 *
 * Uso:
 *   const { suscrito, suscribirse, desuscribirse, soportado } = usePushNotifications();
 *
 * Llama a suscribirse() cuando el usuario hace login o desde la UI.
 * El service worker (sw.ts) maneja el evento push y muestra la notificación.
 */
import { useCallback, useEffect, useState } from "react";
import { api } from "../lib/api";

function urlBase64ToUint8Array(base64String: string): Uint8Array {
  const padding = "=".repeat((4 - (base64String.length % 4)) % 4);
  const base64 = (base64String + padding).replace(/-/g, "+").replace(/_/g, "/");
  const rawData = atob(base64);
  return Uint8Array.from([...rawData].map((c) => c.charCodeAt(0)));
}

export function usePushNotifications() {
  const [soportado, setSoportado] = useState(false);
  const [suscrito, setSuscrito] = useState(false);
  const [cargando, setCargando] = useState(false);

  useEffect(() => {
    setSoportado("serviceWorker" in navigator && "PushManager" in window);
  }, []);

  const suscribirse = useCallback(async () => {
    if (!soportado) return;
    setCargando(true);
    try {
      // Obtener clave pública VAPID del backend
      const { data } = await api.get<{ public_key: string }>("/push/vapid-public-key");
      const applicationServerKey = urlBase64ToUint8Array(data.public_key);

      const reg = await navigator.serviceWorker.ready;
      const subscription = await reg.pushManager.subscribe({
        userVisibleOnly: true,
        applicationServerKey: applicationServerKey.buffer as ArrayBuffer,
      });

      await api.post("/push/subscribe", { subscription: subscription.toJSON() });
      setSuscrito(true);
    } catch (err) {
      console.error("Error al suscribirse a push:", err);
    } finally {
      setCargando(false);
    }
  }, [soportado]);

  const desuscribirse = useCallback(async () => {
    if (!soportado) return;
    setCargando(true);
    try {
      const reg = await navigator.serviceWorker.ready;
      const subscription = await reg.pushManager.getSubscription();
      if (subscription) {
        await api.post("/push/unsubscribe", { subscription: subscription.toJSON() });
        await subscription.unsubscribe();
        setSuscrito(false);
      }
    } catch (err) {
      console.error("Error al desuscribirse:", err);
    } finally {
      setCargando(false);
    }
  }, [soportado]);

  // Verificar si ya hay suscripción activa
  useEffect(() => {
    if (!soportado) return;
    navigator.serviceWorker.ready.then((reg) =>
      reg.pushManager.getSubscription().then((sub) => setSuscrito(!!sub))
    );
  }, [soportado]);

  return { suscrito, suscribirse, desuscribirse, soportado, cargando };
}
