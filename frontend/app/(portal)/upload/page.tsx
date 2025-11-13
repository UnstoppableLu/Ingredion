"use client";

import { useState } from "react";

export default function UploadPage() {
  const [file, setFile] = useState<File | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [success, setSuccess] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFile(e.target.files?.[0] || null);
    setSuccess(false);
  };

  const handleUpload = async () => {
    if (!file) return;

    setIsUploading(true);

    // Simulate backend upload delay
    setTimeout(() => {
      setIsUploading(false);
      setSuccess(true);
    }, 1500);
  };

  return (
    <main className="min-h-screen bg-black text-white p-10">
      <h1 className="text-3xl font-bold text-green-500 mb-6">
        Upload Sustainability Report
      </h1>

      {/* Upload Card */}
      <div className="bg-gray-900 border border-gray-700 rounded-xl p-8 w-full max-w-xl">
        
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
          disabled={!file || isUploading}
          className={`mt-5 w-full py-3 rounded-lg font-semibold transition ${
            !file || isUploading
              ? "bg-gray-700 text-gray-500 cursor-not-allowed"
              : "bg-green-600 hover:bg-green-700"
          }`}
        >
          {isUploading ? "Uploading..." : "Upload"}
        </button>

        {/* Success message */}
        {success && (
          <p className="text-green-500 mt-4 font-semibold">
            ✔ The report has been uploaded successfully (placeholder mock).
          </p>
        )}
      </div>
    </main>
  );
}