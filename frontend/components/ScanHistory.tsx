'use client';
import { useState, useEffect } from 'react';
import axios from 'axios';
import { History, ExternalLink } from 'lucide-react';

interface ScanHistoryItem {
  scan_id: string;
  input_type: string;
  target_value: string;
  status: string;
  start_time: string;
  end_time: string;
}

export default function ScanHistory() {
  const [scans, setScans] = useState<ScanHistoryItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchScanHistory();
  }, []);

  const fetchScanHistory = async () => {
    try {
      const res = await axios.get('http://localhost:5001/api/scans/history');
      setScans(res.data);
    } catch (err) {
      console.error('Failed to fetch scan history:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  const statusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'text-green-600 bg-green-100';
      case 'running': return 'text-blue-600 bg-blue-100';
      case 'error': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  if (loading) {
    return <div className="text-center py-8">Loading scan history...</div>;
  }

  return (
    <div className="bg-white rounded-2xl shadow-lg p-6">
      <div className="flex items-center gap-3 mb-6">
        <History className="w-6 h-6 text-blue-600" />
        <h2 className="text-2xl font-bold text-gray-800">Scan History</h2>
      </div>

      {scans.length === 0 ? (
        <p className="text-gray-500 text-center py-8">No scan history found.</p>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full table-auto">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">Scan ID</th>
                <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">Target</th>
                <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">Status</th>
                <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">Start Time</th>
                <th className="px-4 py-3 text-left text-sm font-semibold text-gray-700">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {scans.map((scan) => (
                <tr key={scan.scan_id} className="hover:bg-gray-50">
                  <td className="px-4 py-3 text-sm font-mono text-gray-600">
                    {scan.scan_id.slice(0, 8)}...
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-700">
                    {scan.target_value}
                  </td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${statusColor(scan.status)}`}>
                      {scan.status}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-600">
                    {formatDate(scan.start_time)}
                  </td>
                  <td className="px-4 py-3">
                    <button
                      onClick={() => window.location.href = `/scan/${scan.scan_id}`}
                      className="flex items-center gap-1 text-blue-600 hover:text-blue-800 text-sm"
                    >
                      <ExternalLink className="w-4 h-4" />
                      View Details
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}