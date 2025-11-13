"use client";

export default function DashboardPage() {
  return (
    <main className="bg-black text-white min-h-screen p-8 space-y-12">
      {/* HEADER */}
      <header className="text-center">
        <h1 className="text-4xl font-bold text-green-500 mb-2">
          Ingredion Sustainability Dashboard
        </h1>
        <p className="text-gray-400">
          View Ingredion metrics and compare with other companies.
        </p>
      </header>

      {/* SECTION 1 — INGREDION METRICS */}
      <section className="bg-gray-900 rounded-xl p-6 shadow-lg">
        <h2 className="text-2xl font-semibold text-green-400 mb-6">
          Ingredion Metrics
        </h2>

        <div className="grid grid-cols-3 gap-6">
          <div className="bg-gray-800 p-4 rounded-lg text-center">
            <p className="text-gray-400">CO₂ Emissions</p>
            <p className="text-3xl font-bold text-green-400">12,000 tons</p>
          </div>
          <div className="bg-gray-800 p-4 rounded-lg text-center">
            <p className="text-gray-400">Renewable Energy</p>
            <p className="text-3xl font-bold text-green-400">47 %</p>
          </div>
          <div className="bg-gray-800 p-4 rounded-lg text-center">
            <p className="text-gray-400">Water Usage</p>
            <p className="text-3xl font-bold text-green-400">150 L/ton</p>
          </div>
        </div>

        <div className="mt-8 h-64 flex items-center justify-center bg-gray-800 rounded-lg text-gray-500">
          Placeholder for Ingredion chart
        </div>
      </section>

      {/* SECTION 2 — COMPANY COMPARISON */}
      <section className="bg-gray-900 rounded-xl p-6 shadow-lg">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-semibold text-green-400">
            Company Comparison
          </h2>

          <select
            className="bg-gray-800 text-white border border-green-600 rounded p-2"
            defaultValue="PepsiCo"
          >
            <option>PepsiCo</option>
            <option>Unilever</option>
            <option>Nestlé</option>
            <option>Kraft Heinz</option>
          </select>
        </div>

        <div className="grid grid-cols-3 gap-6">
          <div className="bg-gray-800 p-4 rounded-lg text-center">
            <p className="text-gray-400">CO₂ Emissions</p>
            <p className="text-3xl font-bold text-blue-400">18,200 tons</p>
          </div>
          <div className="bg-gray-800 p-4 rounded-lg text-center">
            <p className="text-gray-400">Renewable Energy</p>
            <p className="text-3xl font-bold text-blue-400">46 %</p>
          </div>
          <div className="bg-gray-800 p-4 rounded-lg text-center">
            <p className="text-gray-400">Water Usage</p>
            <p className="text-3xl font-bold text-blue-400">120 L/ton</p>
          </div>
        </div>

        <div className="mt-8 h-64 flex items-center justify-center bg-gray-800 rounded-lg text-gray-500">
          Placeholder for company chart
        </div>
      </section>
    </main>
  );
}