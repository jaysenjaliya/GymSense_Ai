// Authenticated home: "Start Today's Session" (dummy/disabled — future feature),
// "Upload Today's Session" (primary), recent analytics, workout history preview.
export default function Dashboard() {
  // TODO: cards + recent analytics; keep the streaming button disabled for now
  return (
    <div className="p-8">
      <h1 className="text-xl font-semibold">Dashboard</h1>
      <button disabled title="Coming soon">Start Today's Session</button>
    </div>
  );
}
