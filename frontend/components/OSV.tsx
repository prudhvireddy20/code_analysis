// ... existing imports ...

type OSVProps = {
  results: {
    tool: string;
    package?: string;
    version?: string;
    ecosystem?: string;
    id?: string;
    severity?: string;
    summary?: string;
    details?: string;
    status?: string;
    error?: string;
  }[];
};

const severityColor = (severity?: string) => {
  if (!severity) return "bg-gray-100 text-gray-700";
  
  const severityStr = severity.toString().toLowerCase();
  
  if (severityStr.includes("critical") || severityStr.includes("high") || (severityStr.includes("cvss_v3") && parseFloat(severityStr) >= 7.0)) {
    return "bg-red-100 text-red-700";
  } else if (severityStr.includes("medium") || (severityStr.includes("cvss_v3") && parseFloat(severityStr) >= 4.0)) {
    return "bg-yellow-100 text-yellow-700";
  } else if (severityStr.includes("low") || (severityStr.includes("cvss_v3") && parseFloat(severityStr) > 0)) {
    return "bg-green-100 text-green-700";
  } else {
    return "bg-gray-100 text-gray-700";
  }
};

export default function OSV({ results }: OSVProps) {
  if (!results || results.length === 0) {
    return <p className="text-gray-500">No OSV scan results available.</p>;
  }

  return (
    <div className="grid gap-4">
      {results.map((item, idx) => (
        <div
          key={idx}
          className="border rounded-2xl p-4 shadow-sm hover:shadow-md transition bg-white"
        >
          {item.error ? (
            <p className="text-red-600 font-semibold">❌ Error: {item.error}</p>
          ) : item.status === "No vulnerabilities found" ? (
            <p className="text-green-700 font-semibold">
              ✅ {item.package}@{item.version} ({item.ecosystem}) - No vulnerabilities found
            </p>
          ) : (
            <>
              <div className="flex justify-between items-center mb-2">
                <h3 className="font-bold text-lg text-red-700">
                  ⚠️ {item.package}@{item.version} ({item.ecosystem})
                </h3>
                <span className={`px-2 py-1 rounded-full text-xs font-semibold ${severityColor(item.severity)}`}>
                  {item.severity || "UNKNOWN"}
                </span>
              </div>
              
              <div className="mb-2">
                <strong>CVE: </strong>
                <span className="font-mono text-sm">{item.id || "N/A"}</span>
              </div>
              
              {item.summary && (
                <div className="mb-2">
                  <strong>Summary: </strong>
                  <span>{item.summary}</span>
                </div>
              )}
              
              {item.details && item.details !== item.summary && (
                <div className="mb-2">
                  <strong>Details: </strong>
                  <span className="text-sm">{item.details}</span>
                </div>
              )}
            </>
          )}
        </div>
      ))}
    </div>
  );
}