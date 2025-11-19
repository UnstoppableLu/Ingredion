"use client";

import { useEffect, useState } from "react";
import axios from "axios";

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [company, setCompany] = useState("");
  const [year, setYear] = useState("");
  const [isUploading, setIsUploading] = useState(false);
  const [success, setSuccess] = useState(false);

  const [metrics, setMetrics] = useState<any[] | null>(null);
  const [allReports, setAllReports] = useState<any[]>([]);
  const [combinedMetrics, setCombinedMetrics] = useState<any[]>([]);
  
  const [selectedFile, setSelectedFile] = useState("All");
  const uniqueFiles = ["All", ...new Set(combinedMetrics.map(m => m.source_file))];
  const filteredMetrics =
    selectedFile === "All"
      ? combinedMetrics
      : combinedMetrics.filter((m) => m.source_file === selectedFile);


  const [replacePrompt, setReplacePrompt] = useState(false);
  const [pendingFormData, setPendingFormData] = useState<FormData | null>(null);
  const [statusMessage, setStatusMessage] = useState("");

  useEffect(() => {
    axios.get("http://127.0.0.1:8000/api/list_extracted")
      .then((res) => setAllReports(res.data.reports || []))
      .catch(() => {});

    axios.get("http://127.0.0.1:8000/api/all_metrics")
      .then((res) => setCombinedMetrics(res.data.metrics || []))
      .catch(() => {});
  }, []);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFile(e.target.files?.[0] || null);
    setSuccess(false);
    setMetrics(null);
  };

  const uploadToBackend = async (formData: FormData, force = false) => {
    try {
      setIsUploading(true);
      setStatusMessage("Uploading to server...");
      setSuccess(false);

      formData.set("force", String(force));

      const response = await axios.post(
        "http://127.0.0.1:8000/api/extract",
        formData,
        { headers: { "Content-Type": "multipart/form-data" } }
      );

      const data = response.data;

      if (data.status === "exists" && !force) {
        setReplacePrompt(true);
        setPendingFormData(formData);
        setIsUploading(false);
        return;
      }

      if (data.status === "success") {
        setMetrics(data.metrics || []);
        setSuccess(true);
        setStatusMessage("File uploaded and processed successfully.");

        const list = await axios.get("http://127.0.0.1:8000/api/list_extracted");
        setAllReports(list.data.reports || []);

        const all = await axios.get("http://127.0.0.1:8000/api/all_metrics");
        setCombinedMetrics(all.data.metrics || []);
      }

    } catch (err) {
      console.error(err);
      setStatusMessage("Upload failed.");
    } finally {
      setIsUploading(false);
    }
  };

  const handleUpload = async () => {
    if (!file || !company || !year) return;

    const formData = new FormData();
    formData.append("file", file);
    formData.append("company", company);
    formData.append("year", year);

    await uploadToBackend(formData, false);
  };

  const confirmReplace = async () => {
    if (!pendingFormData) return;
    setReplacePrompt(false);
    await uploadToBackend(pendingFormData, true);
  };

  const cancelReplace = () => {
    setReplacePrompt(false);
    setPendingFormData(null);
    setStatusMessage("Upload canceled.");
  };

  return (
    <main className="min-h-screen bg-black text-white p-10">

      <h1 className="text-3xl font-bold text-green-500 mb-10 text-center">
        Upload Sustainability Report
      </h1>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">

        <div className="bg-gray-900 border border-gray-700 rounded-xl p-8 w-full max-w-xl mx-auto">
          <label className="block mb-3">
            <span className="text-gray-300">Company Name</span>
            <input
              type="text"
              value={company}
              onChange={(e) => setCompany(e.target.value)}
              className="mt-1 w-full p-2 bg-gray-800 border border-gray-700 rounded-lg text-white"
            />
          </label>

          <label className="block mb-5">
            <span className="text-gray-300">Report Year</span>
            <input
              type="number"
              value={year}
              onChange={(e) => setYear(e.target.value)}
              className="mt-1 w-full p-2 bg-gray-800 border border-gray-700 rounded-lg text-white"
            />
          </label>

          <label className="flex flex-col items-center justify-center h-40 border-2 border-dashed 
            border-gray-600 rounded-xl cursor-pointer hover:border-green-500 transition">
            <input type="file" accept="application/pdf" className="hidden" onChange={handleFileChange} />
            <span className="text-gray-300">Click to select a PDF file</span>
          </label>

          {file && (
            <p className="text-green-400 mt-3 font-semibold">
              Selected: {file.name}
            </p>
          )}

          <button
            onClick={handleUpload}
            disabled={!file || !company || !year || isUploading}
            className={`mt-5 w-full py-3 rounded-lg font-semibold transition ${
              !file || !company || !year || isUploading
                ? "bg-gray-700 text-gray-500 cursor-not-allowed"
                : "bg-green-600 hover:bg-green-700"
            }`}
          >
            {isUploading ? "Uploading..." : "Upload"}
          </button>

          {statusMessage && (
            <p className="text-yellow-400 mt-4 font-semibold">{statusMessage}</p>
          )}
        </div>

        <div className="bg-gray-900 border border-gray-700 rounded-xl p-6 overflow-auto max-h-[600px]">
          <h2 className="text-2xl font-bold text-blue-400 mb-4">📁 Extracted Reports</h2>

          <div className="grid grid-cols-3 gap-3 font-bold text-gray-300 border-b border-gray-700 pb-2">
            <div>Company</div>
            <div>Year</div>
            <div>File</div>
          </div>

          {allReports.map((r, i) => (
            <div key={i} className="grid grid-cols-3 gap-3 border-b border-gray-800 py-2 text-gray-200">
              <div>{r.company}</div>
              <div>{r.year}</div>
              <div className="truncate">{r.path}</div>
            </div>
          ))}
        </div>
      </div>

      <div className="mt-16 bg-gray-900 border border-gray-700 p-6 rounded-xl">

        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-bold text-green-400">
            📊 All Extracted Metrics
          </h2>

          <div className="flex items-center gap-2">
            <span className="text-gray-300 font-semibold">Filter:</span>
            <select
              value={selectedFile}
              onChange={(e) => setSelectedFile(e.target.value)}
              className="p-2 bg-gray-800 border border-gray-700 rounded-lg text-white"
            >
              {uniqueFiles.map((file, idx) => (
                <option key={idx} value={file}>
                  {file}
                </option>
              ))}
            </select>
          </div>
        </div>


        <div className="grid grid-cols-6 gap-3 font-bold text-gray-300 border-b border-gray-700 pb-2">
          <div>Metric</div>
          <div>Value</div>
          <div>Unit</div>
          <div>Year</div>
          <div>Source Page</div>
          <div>File</div>
        </div>

        <div className="max-h-[450px] overflow-y-scroll pr-2 scrollbar-thin scrollbar-thumb-gray-600 scrollbar-track-gray-800">
          {filteredMetrics.map((m, i) => (
            <div key={i} className="grid grid-cols-6 gap-3 border-b border-gray-800 py-2 text-gray-200">
              <div>{m.metric_name}</div>
              <div>{m.value}</div>
              <div>{m.unit}</div>
              <div>{m.year}</div>
              <div>{m.source_page}</div>
              <div>{m.source_file}</div>
            </div>
          ))}
        </div>
      </div>

      {replacePrompt && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center">
          <div className="bg-gray-800 p-6 rounded-xl border border-gray-600 max-w-sm">
            <h2 className="text-xl font-bold text-red-400 mb-3">File Already Exists</h2>
            <p className="text-gray-300 mb-5">
              A report for this company and year already exists.<br />Replace it?
            </p>

            <div className="flex gap-3">
              <button
                onClick={confirmReplace}
                className="bg-red-600 hover:bg-red-700 px-4 py-2 rounded-lg font-semibold"
              >
                Replace
              </button>
              <button
                onClick={cancelReplace}
                className="bg-gray-600 hover:bg-gray-700 px-4 py-2 rounded-lg font-semibold"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

    </main>
  );
}