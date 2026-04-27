import { DashboardWidgets } from "../widgets/dashboard-widgets";

export function Home() {
  return (
    <div className="mx-auto w-full max-w-6xl p-4">
      <h1 className="mb-4 text-2xl font-semibold">Document Dashboard</h1>
      <DashboardWidgets />
    </div>
  );
}
