"use client";
import { useState } from 'react';

export default function ScanResults({ results }: { results: any }) {
  const [tab, setTab] = useState("osv");

  const renderTab = () => {
    const data = results[tab];
    return (
      <pre className="bg-gray-900 text-white p-4 rounded overflow-x-auto text-sm">
        {data ? JSON.stringify(data, null, 2) : `No results for ${tab.toUpperCase()}.`}
      </pre>
    );
  };

  return (
    <div>
      <div className="flex gap-4 border-b mb-4">
        {["osv", "codeql", "gitleaks", "syft", "noir","semgrep"].map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`py-2 px-4 border-b-2 ${
              tab === t ? "border-blue-600 font-bold" : "border-transparent"
            }`}
          >
            {t.toUpperCase()}
          </button>
        ))}
      </div>
      {renderTab()}
    </div>
  );
}
