// Fixed, animated gradient "aurora" blobs + subtle grid — the app's ambient backdrop.
export default function AuroraBackground() {
  return (
    <div className="pointer-events-none fixed inset-0 -z-10 overflow-hidden">
      {/* deep base */}
      <div className="absolute inset-0 bg-ink-950" />

      {/* animated color blobs */}
      <div className="absolute -left-32 -top-24 h-[38rem] w-[38rem] animate-blob rounded-full bg-emerald-500/20 blur-[120px]" />
      <div className="absolute right-[-10rem] top-10 h-[34rem] w-[34rem] animate-blob rounded-full bg-violet-600/20 blur-[120px] [animation-delay:4s]" />
      <div className="absolute bottom-[-12rem] left-1/3 h-[36rem] w-[36rem] animate-blob rounded-full bg-cyan-500/10 blur-[120px] [animation-delay:8s]" />

      {/* faint grid overlay */}
      <div
        className="absolute inset-0 opacity-[0.15]"
        style={{
          backgroundImage:
            "linear-gradient(to right, rgba(148,163,184,0.08) 1px, transparent 1px), linear-gradient(to bottom, rgba(148,163,184,0.08) 1px, transparent 1px)",
          backgroundSize: "48px 48px",
          maskImage: "radial-gradient(ellipse at center, black 40%, transparent 75%)",
        }}
      />
    </div>
  );
}
