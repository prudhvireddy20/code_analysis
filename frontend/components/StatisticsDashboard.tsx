'use client';
import { useState, useEffect } from 'react';
import axios from 'axios';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { AlertTriangle, Shield, Package, Key, TrendingUp, RefreshCw } from 'lucide-react';

interface Scan {
  scan_id: string;
  status: string;
  results: any;
  start_time: string;
}

interface Statistics {
  totalScans: number;
  totalVulnerabilities: number;
  scansByDay: { date: string; count: number; vulnerabilities: number }[];
  severityDistribution: { name: string; value: number }[];
  toolFindings: { tool: string; count: number }[];
}

const SEVERITY_COLORS = {
  CRITICAL: '#dc2626',
  HIGH: '#ea580c',
  MEDIUM: '#ca8a04',
  LOW: '#16a34a',
  UNKNOWN: '#6b7280'
};

export default function StatisticsDashboard() {
  const [stats, setStats] = useState<Statistics | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    fetchStatistics();
  }, []);

  const fetchStatistics = async () => {
    try {
      const res = await axios.get('http://localhost:5001/api/scans/history');
      const scans: Scan[] = res.data;
      
      const statistics = calculateStatistics(scans);
      setStats(statistics);
    } catch (err) {
      console.error('Failed to fetch statistics:', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await fetchStatistics();
  };

  const calculateStatistics = (scans: Scan[]): Statistics => {
    // Filter only completed scans with results
    const completedScans = scans.filter(scan => 
      scan.status === 'completed' && scan.results
    );

    // Calculate scans by day
    const scansByDayMap: Record<string, { count: number; vulnerabilities: number }> = {};
    
    completedScans.forEach(scan => {
      const date = new Date(scan.start_time).toLocaleDateString();
      if (!scansByDayMap[date]) {
        scansByDayMap[date] = { count: 0, vulnerabilities: 0 };
      }
      scansByDayMap[date].count += 1;
      scansByDayMap[date].vulnerabilities += countVulnerabilities(scan.results);
    });

    const scansByDay = Object.entries(scansByDayMap).map(([date, data]) => ({
      date,
      count: data.count,
      vulnerabilities: data.vulnerabilities
    })).sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());

    // Calculate severity distribution
    const severityCounts: Record<string, number> = {};
    completedScans.forEach(scan => {
      if (scan.results.osv) {
        scan.results.osv.forEach((vuln: any) => {
          if (vuln.severity) {
            const severity = vuln.severity.toUpperCase();
            severityCounts[severity] = (severityCounts[severity] || 0) + 1;
          }
        });
      }
    });

    const severityDistribution = Object.entries(severityCounts).map(([name, value]) => ({
      name,
      value
    }));

    // Calculate tool findings
    const toolCounts: Record<string, number> = {};
    completedScans.forEach(scan => {
      Object.entries(scan.results).forEach(([tool, findings]) => {
        if (Array.isArray(findings)) {
          toolCounts[tool] = (toolCounts[tool] || 0) + findings.length;
        }
      });
    });

    const toolFindings = Object.entries(toolCounts).map(([tool, count]) => ({
      tool: tool.toUpperCase(),
      count
    }));

    return {
      totalScans: completedScans.length,
      totalVulnerabilities: completedScans.reduce((total, scan) => total + countVulnerabilities(scan.results), 0),
      scansByDay,
      severityDistribution,
      toolFindings
    };
  };

  const countVulnerabilities = (results: any): number => {
    let count = 0;
    if (results.osv) count += results.osv.filter((v: any) => !v.status).length;
    if (results.codeql) count += results.codeql.length;
    if (results.gitleaks) count += results.gitleaks.length;
    return count;
  };

  if (loading) {
    return <div className="text-center py-8">Loading statistics...</div>;
  }

  if (!stats || stats.totalScans === 0) {
    return (
      <div className="text-center py-12 bg-gray-50 rounded-lg">
        <TrendingUp className="w-12 h-12 text-gray-400 mx-auto mb-4" />
        <p className="text-gray-500">No scan data available for statistics</p>
        <p className="text-sm text-gray-400">Run some scans to see trends and metrics</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header with Refresh Button */}
      <div className="flex items-center justify-between">
        <h2 className="text-xl font-bold text-gray-800">Security Analytics</h2>
        <button
          onClick={handleRefresh}
          disabled={refreshing}
          className="flex items-center gap-2 px-3 py-2 text-sm text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded-lg transition disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
          {refreshing ? 'Refreshing...' : 'Refresh'}
        </button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
          <div className="flex items-center gap-3">
            <Shield className="w-8 h-8 text-blue-600" />
            <div>
              <h3 className="text-2xl font-bold text-blue-800">{stats.totalScans}</h3>
              <p className="text-blue-600">Total Scans</p>
            </div>
          </div>
        </div>

        <div className="bg-red-50 p-4 rounded-lg border border-red-200">
          <div className="flex items-center gap-3">
            <AlertTriangle className="w-8 h-8 text-red-600" />
            <div>
              <h3 className="text-2xl font-bold text-red-800">{stats.totalVulnerabilities}</h3>
              <p className="text-red-600">Vulnerabilities Found</p>
            </div>
          </div>
        </div>

        <div className="bg-green-50 p-4 rounded-lg border border-green-200">
          <div className="flex items-center gap-3">
            <TrendingUp className="w-8 h-8 text-green-600" />
            <div>
              <h3 className="text-2xl font-bold text-green-800">
                {stats.totalScans > 0 ? (stats.totalVulnerabilities / stats.totalScans).toFixed(1) : 0}
              </h3>
              <p className="text-green-600">Avg. per Scan</p>
            </div>
          </div>
        </div>
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Scans & Vulnerabilities Over Time */}
        <div className="bg-white p-4 rounded-lg border">
          <h3 className="font-semibold mb-4 text-gray-800">Scans & Vulnerabilities Over Time</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={stats.scansByDay}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="count" name="Scans" fill="#3b82f6" />
              <Bar dataKey="vulnerabilities" name="Vulnerabilities" fill="#ef4444" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Severity Distribution */}
        <div className="bg-white p-4 rounded-lg border">
          <h3 className="font-semibold mb-4 text-gray-800">Vulnerability Severity</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={stats.severityDistribution}
                cx="50%"
                cy="50%"
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
                label={({ name, value }) => `${name}: ${value}`}
              >
                {stats.severityDistribution.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={SEVERITY_COLORS[entry.name as keyof typeof SEVERITY_COLORS] || '#6b7280'} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Tools Findings */}
        <div className="bg-white p-4 rounded-lg border lg:col-span-2">
          <h3 className="font-semibold mb-4 text-gray-800">Findings by Tool</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={stats.toolFindings}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="tool" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="count" fill="#8b5cf6" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}