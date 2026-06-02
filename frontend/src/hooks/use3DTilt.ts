import { useRef, useState, useCallback } from "react";
import type { CSSProperties, MouseEvent } from "react";

export function use3DTilt(intensity = 12) {
  const ref = useRef<HTMLDivElement>(null);
  const [style, setStyle] = useState<CSSProperties>({
    transform: "perspective(900px) rotateX(0deg) rotateY(0deg) translateZ(0px)",
    transition: "transform 0.4s ease-out",
    willChange: "transform",
  });

  const onMouseMove = useCallback(
    (e: MouseEvent) => {
      const el = ref.current;
      if (!el) return;
      const { left, top, width, height } = el.getBoundingClientRect();
      const x = ((e.clientX - left) / width  - 0.5) * intensity;
      const y = ((e.clientY - top)  / height - 0.5) * intensity;
      setStyle({
        transform: `perspective(900px) rotateY(${x}deg) rotateX(${-y}deg) translateZ(10px)`,
        transition: "transform 0.08s ease-out",
        willChange: "transform",
      });
    },
    [intensity],
  );

  const onMouseLeave = useCallback(() => {
    setStyle({
      transform: "perspective(900px) rotateX(0deg) rotateY(0deg) translateZ(0px)",
      transition: "transform 0.45s ease-out",
      willChange: "transform",
    });
  }, []);

  return { ref, style, onMouseMove, onMouseLeave };
}
