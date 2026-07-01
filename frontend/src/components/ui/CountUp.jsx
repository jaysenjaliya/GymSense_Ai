// Animated number that counts up from 0 when mounted / when value changes.
import { useEffect, useRef, useState } from "react";

export default function CountUp({ value, duration = 1100, decimals = 0, prefix = "", suffix = "" }) {
  const [display, setDisplay] = useState(0);
  const frame = useRef();

  useEffect(() => {
    const to = Number(value) || 0;
    let startTime;
    const tick = (t) => {
      if (!startTime) startTime = t;
      const progress = Math.min((t - startTime) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3); // easeOutCubic
      setDisplay(to * eased);
      if (progress < 1) frame.current = requestAnimationFrame(tick);
    };
    frame.current = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frame.current);
  }, [value, duration]);

  const text = display.toLocaleString(undefined, {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
  return (
    <span>
      {prefix}
      {text}
      {suffix}
    </span>
  );
}
