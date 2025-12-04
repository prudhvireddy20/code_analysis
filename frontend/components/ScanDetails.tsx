'use client';
import { useState, useEffect } from 'react';
import { useParams, useRouter } from 'next/navigation';
import axios from 'axios';
import { ArrowLeft, AlertTriangle, Shield, Package, Key, AlertCircleIcon, ScanEye } from 'lucide-react';
import OSV from './OSV';
import SBOM from './SBOM';
import Noir from './NOIR'
import CodeQLResults from './CodeQLResults';
import SSemgrepResults from './SEMGREP';
import Secrets from './Secrets';
import SemgrepResults from './SEMGREP';

interface ScanDetails {
  scan_id: string;
  input_type: string;
  target_value: string;
  status: string;
  results: any;
  start_time: string;
  end_time: string;
  error_message: string;
}

export default function ScanDetails() {
  const params = useParams();
  const router = useRouter();
  const scanId = params.scanId as string;
  
  const [scan, setScan] = useState<ScanDetails | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    fetchScanDetails();
  }, [scanId]);

  const fetchScanDetails = async () => {
    try {
      const res = await axios.get(`http://localhost:5001/api/scans/${scanId}`);
      setScan(res.data);
    } catch (err) {
      console.error('Failed to fetch scan details:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="text-center py-8">Loading scan details...</div>;
  }

  if (!scan) {
    return <div className="text-center py-8">Scan not found</div>;
  }

  const tabs = [
    { id: 'overview', label: 'Overview', icon: Shield },
    { id: 'osv', label: 'OSV', icon: AlertTriangle },
    { id: 'sbom', label: 'SBOM', icon: Package },
    { id: 'codeql', label: 'CodeQL', icon: Shield },
    { id: 'gitleaks', label: 'Gitleaks', icon: Key },
    { id: 'noir', label: 'Noir', icon: ScanEye},
    { id: 'semgrep', label: 'Semgrep', icon: ScanEye}
  ];

  const getVulnerabilityCount = () => {
    if (!scan.results) return 0;
    let count = 0;
    if (scan.results.osv) count += scan.results.osv.filter((item: any) => !item.status).length;
    if (scan.results.codeql) count += scan.results.codeql.length;
    if (scan.results.gitleaks) count += scan.results.gitleaks.length;
    if (scan.results.noir) count += scan.results.noir.length;
    return count;
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="bg-white rounded-2xl shadow-lg p-6">
        {/* Header */}
        <div className="flex items-center gap-4 mb-6">
          <button
            onClick={() => router.back()}
            className="p-2 hover:bg-gray-100 rounded-lg"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <h1 className="text-2xl font-bold text-gray-800">Scan Details</h1>
            <p className="text-gray-600 text-sm">Scan ID: {scan.scan_id}</p>
          </div>
        </div>

        {/* Scan Info */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="bg-blue-50 p-4 rounded-lg">
            <h3 className="font-semibold text-blue-800">Target</h3>
            <p className="truncate">{scan.target_value}</p>
          </div>
          <div className="bg-green-50 p-4 rounded-lg">
            <h3 className="font-semibold text-green-800">Status</h3>
            <p className="capitalize">{scan.status}</p>
          </div>
          <div className="bg-purple-50 p-4 rounded-lg">
            <h3 className="font-semibold text-purple-800">Vulnerabilities</h3>
            <p>{getVulnerabilityCount()} found</p>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex gap-4 border-b mb-4">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2 px-4 py-2 border-b-2 ${
                  activeTab === tab.id 
                    ? 'border-blue-600 text-blue-700 font-semibold' 
                    : 'border-transparent text-gray-600'
                }`}
              >
                <Icon className="w-4 h-4" />
                {tab.label}
              </button>
            );
          })}
        </div>

        {/* Tab Content */}
        <div>
          {activeTab === 'overview' && (
            <div>
              <h3 className="text-lg font-semibold mb-4">Scan Information</h3>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <strong>Start Time:</strong> {new Date(scan.start_time).toLocaleString()}
                </div>
                <div>
                  <strong>End Time:</strong> {scan.end_time ? new Date(scan.end_time).toLocaleString() : 'N/A'}
                </div>
                <div>
                  <strong>Input Type:</strong> {scan.input_type}
                </div>
                <div>
                  <strong>Status:</strong> {scan.status}
                </div>
              </div>
              
              {scan.error_message && (
                <div className="mt-4 p-4 bg-red-50 rounded-lg">
                  <h4 className="font-semibold text-red-800">Error:</h4>
                  <p className="text-red-600">{scan.error_message}</p>
                </div>
              )}
            </div>
          )}

          {activeTab === 'osv' && scan.results?.osv && (
            <OSV results={scan.results.osv} />
          )}

          {activeTab === 'sbom' && scan.results?.syft && (
            <SBOM data={scan.results.syft} />
          )}

          {activeTab === 'codeql' && scan.results?.codeql && (
            <CodeQLResults data={scan.results.codeql} />
          )}

          {activeTab === 'gitleaks' && scan.results?.gitleaks && (
            <Secrets data={scan.results.gitleaks} />
          )}

         {activeTab === 'noir' && (
          <Noir data={scan.results?.noir || []} />
          )}

          {activeTab === 'semgrep' && (
          <SemgrepResults data={scan.results?.semgrep || []} />
          )}

        </div>
      </div>
    </div>
  );
}