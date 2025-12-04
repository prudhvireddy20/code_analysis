'use client';
import { useState } from 'react';
import ScanInput from './ScanInput';
import Secrets from "@/components/Secrets";
import CodeQLResults from "@/components/CodeQLResults";
import SBOM from "@/components/SBOM";
import OSV from "@/components/OSV";
import NOIR from './NOIR';
import ScanHistory from './ScanHistory';
import StatisticsDashboard from './StatisticsDashboard';
import { Loader2 } from "lucide-react";
import SemgrepResults from './SEMGREP';

export default function Dashboard({ token }: { token: string }) {
  const [activeTab, setActiveTab] = useState('overview');
  const [scanResults, setScanResults] = useState<any>({});
  const [loadingTabs, setLoadingTabs] = useState<any>({
    osv: false,
    sbom: false,
    codeql: false,
    gitleaks: false,
    noir: false,
    semgrep : false
  });

  const handleScanStart = () => {
    setLoadingTabs({
      osv: true,
      sbom: true,
      codeql: true,
      gitleaks: true,
      noir: true,
      semgrep : true
    });
  };

  const handleScanComplete = (data: any) => {
    setScanResults(data);
    setLoadingTabs({
      osv: false,
      sbom: false,
      codeql: false,
      gitleaks: false,
      noir: false,
      semgrep : false
    });
  };

  const tabs = ['Overview', 'OSV', 'SBOM', 'CodeQL', 'Gitleaks','Noir', 'Semgrep', 'History'];

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900 flex flex-col">
      {/* Header */}
      <header className="bg-white shadow-lg px-6 py-4 flex justify-between items-center">
        <h1 className="text-3xl font-bold text-blue-700">🔐 Unified Security Dashboard</h1>
        <span className="text-sm text-gray-500">Token: {token}</span>
      </header>

      {/* Tabs */}
      <nav className="flex space-x-4 bg-gradient-to-r from-blue-50 via-blue-100 to-blue-50 px-6 py-2 rounded-b-xl shadow-inner">
        {tabs.map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab.toLowerCase())}
            className={`px-4 py-2 rounded-xl font-semibold transition
              ${activeTab === tab.toLowerCase()
                ? "bg-blue-600 text-white shadow-lg"
                : "bg-white text-gray-700 hover:bg-blue-100"}
            `}
          >
            {tab}
          </button>
        ))}
      </nav>

      {/* Tab Content */}
      <main className="flex-1 p-6 m-6 bg-white rounded-2xl shadow-xl transition">
        {activeTab === 'overview' && (
          <div className="space-y-6">
            <ScanInput
              onScanStart={handleScanStart}
              onScanComplete={handleScanComplete}
            />
            <StatisticsDashboard />
          </div>
        )}

        {activeTab === 'osv' && (
          loadingTabs.osv ? (
            <div className="flex justify-center items-center gap-2 text-gray-600">
              <Loader2 className="animate-spin w-5 h-5" /> Scanning OSV...
            </div>
          ) : scanResults?.osv?.length > 0 ? (
            <OSV results={scanResults.osv} />
          ) : (
            <p className="text-gray-500">Run a scan to see OSV results.</p>
          )
        )}

        {activeTab === "sbom" && (
          loadingTabs.sbom ? (
            <div className="flex justify-center items-center gap-2 text-gray-600">
              <Loader2 className="animate-spin w-5 h-5" /> Generating SBOM...
            </div>
          ) : scanResults?.syft?.length > 0 ? (
            <SBOM data={scanResults.syft} />
          ) : (
            <p className="text-gray-500">Run a scan to see SBOM results.</p>
          )
        )}

        {activeTab === 'codeql' && (
          loadingTabs.codeql ? (
            <div className="flex justify-center items-center gap-2 text-gray-600">
              <Loader2 className="animate-spin w-5 h-5" /> Running CodeQL...
            </div>
          ) : scanResults?.codeql ? (
            <CodeQLResults data={scanResults.codeql} />
          ) : (
            <p className="text-gray-500">Run a scan to see CodeQL results.</p>
          )
        )}

        {activeTab === 'gitleaks' && (
          loadingTabs.gitleaks ? (
            <div className="flex justify-center items-center gap-2 text-gray-600">
              <Loader2 className="animate-spin w-5 h-5" /> Running Gitleaks...
            </div>
          ) : scanResults?.gitleaks ? (
            <Secrets data={scanResults.gitleaks} />
          ) : (
            <p className="text-gray-500">Run a scan to see Gitleaks results.</p>
          )
        )}

         {activeTab === 'noir' && (
          loadingTabs.noir ? (
            <div className="flex justify-center items-center gap-2 text-gray-600">
              <Loader2 className="animate-spin w-5 h-5" /> Running Noir....
            </div>
          ) : scanResults?.noir?.length > 0 ? (
            <NOIR data={scanResults.noir}/>
          ) : (
            <p className="text-gray-500">Run a scan to see Noir results.</p>
          )
        )}

        {activeTab === 'semgrep' && (
          loadingTabs.semgrep ? (
            <div className="flex justify-center items-center gap-2 text-gray-600">
              <Loader2 className="animate-spin w-5 h-5" /> Running Semgrep...
            </div>
          ) : scanResults?.semgrep ? (
            <SemgrepResults data={scanResults.semgrep} />
          ) : (
            <p className="text-gray-500">Run a scan to see Semgrep results.</p>
          )
        )}

        {activeTab === 'history' && (
          <ScanHistory />
        )}
      </main>
    </div>
  );
}