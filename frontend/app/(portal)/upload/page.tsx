"use client";

import { useState } from "react";
import axios from "axios";

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [company, setCompany] = useState("");
  const [year, setYear] = useState("");
  const [isUploading, setIsUploading] = useState(false);
  const [success, setSuccess] = useState(false);

  const [replacePrompt, setReplacePrompt] = useState(false);
  const [pendingFormData, setPendingFormData] = useState<FormData | null>(null);
  const [statusMessage, setStatusMessage] = useState("");

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFile(e.target.files?.[0] || null);
    setSuccess(false);
  };

  const uploadToBackend = async (formData: FormData, force = false) => {
    try {
      setIsUploading(true);
      setStatusMessage("Uploading to server...");

      formData.set("force", String(force)); // Ensure force is included

      const response = await axios.post(
        "http://127.0.0.1:8000/api/extract",
        formData,
        {
          headers: { "Content-Type": "multipart/form-data" },
        }
      );

      const data = response.data;

      if (data.status === "exists" && !force) {
        // Backend says this file exists — ask user if they want to replace it
        setReplacePrompt(true);
        setPendingFormData(formData);
        setIsUploading(false);
        return;
      }

      setSuccess(true);
      setStatusMessage("File uploaded and processed successfully.");
    } catch (err: any) {
      console.error(err);
      setStatusMessage("❌ Upload failed. Check backend.");
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

    await uploadToBackend(formData, false); // first try without force
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
      <h1 className="text-3xl font-bold text-green-500 mb-6">
        Upload Sustainability Report
      </h1>

      {/* Upload Card */}
      <div className="bg-gray-900 border border-gray-700 rounded-xl p-8 w-full max-w-xl">

        {/* Company Name */}
        <label className="block mb-3">
          <span className="text-gray-300">Company Name</span>
          <input
            type="text"
            value={company}
            onChange={(e) => setCompany(e.target.value)}
            className="mt-1 w-full p-2 bg-gray-800 border border-gray-700 rounded-lg text-white"
            placeholder="e.g., Coca Cola"
          />
        </label>

        {/* Year */}
        <label className="block mb-5">
          <span className="text-gray-300">Report Year</span>
          <input
            type="number"
            value={year}
            onChange={(e) => setYear(e.target.value)}
            className="mt-1 w-full p-2 bg-gray-800 border border-gray-700 rounded-lg text-white"
            placeholder="e.g., 2024"
          />
        </label>

        {/* File Picker */}
        <label className="flex flex-col items-center justify-center h-40 border-2 border-dashed border-gray-600 rounded-xl cursor-pointer hover:border-green-500 transition">
          <input type="file" accept="application/pdf" className="hidden" onChange={handleFileChange} />
          <span className="text-gray-300">Click to select a PDF file</span>
        </label>

        {file && (
          <p className="text-green-400 mt-3">
            Selected: <span className="font-semibold">{file.name}</span>
          </p>
        )}

        {/* Upload Button */}
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

        {/* Status message */}
        {statusMessage && (
          <p className="text-yellow-400 mt-4 font-semibold">{statusMessage}</p>
        )}

        {/* Success message */}
        {success && (
          <p className="text-green-500 mt-4 font-semibold">
            ✔ Report processed & saved successfully!
          </p>
        )}
      </div>

      {/* Replace File Modal */}
      {replacePrompt && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center">
          <div className="bg-gray-800 p-6 rounded-xl border border-gray-600 max-w-sm">
            <h2 className="text-xl font-bold text-red-400 mb-3">File Already Exists</h2>
            <p className="text-gray-300 mb-5">
              A report for this company and year already exists.  
              Do you want to replace it?
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