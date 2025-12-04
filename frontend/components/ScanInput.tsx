'use client';
import { useState } from 'react';
import axios from 'axios';
import { Upload, GitBranch, Folder, Play } from "lucide-react";

export default function ScanInput({
  onScanComplete,
  onScanStart
}: {
  onScanComplete: (data: any) => void;
  onScanStart: () => void;
}) {
  const [inputType, setInputType] = useState("git");
  const [value, setValue] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);

  const pollScanResult = async (scanId: string) => {
    try {
      const interval = setInterval(async () => {
        const res = await axios.get(`http://localhost:5001/api/scan-result/${scanId}`);
        if (res.data.status === "done") {
          onScanComplete(res.data.result);
          setLoading(false);
          clearInterval(interval);
        } else if (res.data.status === "error") {
          alert("Scan failed: " + res.data.result);
          setLoading(false);
          clearInterval(interval);
        }
      }, 2000);
    } catch (err: any) {
      alert("Error polling scan result: " + err.message);
      setLoading(false);
    }
  };

  const handleScan = async () => {
    onScanStart();
    setLoading(true);
    try {
      let scanRes;

      if (inputType === "upload" && file) {
        const formData = new FormData();
        formData.append("file", file);
        const uploadRes = await axios.post("http://localhost:5001/api/upload", formData);
        scanRes = await axios.post("http://localhost:5001/api/scan", {
          type: inputType,
          value: uploadRes.data.filename,
        });
      } else {
        scanRes = await axios.post("http://localhost:5001/api/scan", {
          type: inputType,
          value,
        });
        console.log(scanRes)
      }

      const scanId = scanRes.data.scan_id;
      await pollScanResult(scanId);

    } catch (err: any) {
      alert("Scan failed: " + err.message);
      setLoading(false);
    }
  };

  return (
    <div className="bg-white p-6 rounded-2xl shadow-lg flex flex-col gap-4">
      <h2 className="text-2xl font-bold text-blue-700">🚀 Start a Scan</h2>

      <div className="flex gap-3 items-center">
        <select
          value={inputType}
          onChange={(e) => setInputType(e.target.value)}
          className="border rounded-xl p-3 flex-1 bg-gray-50 hover:bg-gray-100 transition"
        >
          <option value="git">Git Repository</option>
          <option value="upload">Upload ZIP</option>
        </select>

        {inputType === "git" && <GitBranch className="w-6 h-6 text-gray-400" />}
        {inputType === "upload" && <Upload className="w-6 h-6 text-gray-400" />}
        
      </div>

      {inputType === "upload" ? (
        <input
          type="file"
          accept=".zip"
          onChange={(e) => setFile(e.target.files?.[0] || null)}
          className="border rounded-xl p-3 w-full bg-gray-50 hover:bg-gray-100 transition"
        />
      ) : (
        <input
          type="text"
          placeholder={inputType === "git" ? "https://github.com/user/repo.git" : "/absolute/path/to/project"}
          value={value}
          onChange={(e) => setValue(e.target.value)}
          className="border rounded-xl p-3 w-full bg-gray-50 hover:bg-gray-100 transition"
        />
      )}

      <button
        onClick={handleScan}
        disabled={loading}
        className={`mt-2 w-full flex items-center justify-center gap-2 px-4 py-3 rounded-xl font-semibold text-white
          ${loading ? "bg-gray-400 cursor-not-allowed" : "bg-blue-600 hover:bg-blue-700 transition"}
        `}
      >
        <Play className="w-5 h-5" />
        {loading ? "Scanning..." : "Start Scan"}
      </button>
    </div>
  );
}