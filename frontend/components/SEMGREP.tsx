'use client';

interface SemgrepIssue {
  path: string;
  start?: { line?: number };
  check_id: string;
  extra?: { message?: string };
}

const ruleColor = "text-red-600 font-semibold";

export default function SemgrepResults({ data }: { data: SemgrepIssue[] }) {
  if (!data || data.length === 0) {
    return <p className="text-green-700 font-semibold">✅ No Semgrep issues found.</p>;
  }

  return (
    <div className="bg-white rounded-2xl shadow-lg p-4 overflow-x-auto">
      <h2 className="text-2xl font-semibold mb-4 text-blue-700">Semgrep Scan Results</h2>
      <table className="min-w-full divide-y divide-gray-200 text-sm">
        <thead className="bg-gray-50">
          <tr>
            {["File", "Line", "Rule", "Message"].map((head) => (
              <th key={head} className="px-4 py-2 text-left font-semibold text-gray-700">{head}</th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-100">
          {data.map((issue, idx) => (
            <tr key={idx} className="hover:bg-gray-50 transition">
              <td className="px-4 py-2 font-mono text-xs">{issue.path}</td>
              <td className="px-4 py-2">{issue.start?.line || "-"}</td>
              <td className={`px-4 py-2 ${ruleColor}`}>{issue.check_id}</td>
              <td className="px-4 py-2">{issue.extra?.message || "-"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
