"use client";

import { useState } from "react";

export default function UploadPage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [message, setMessage] = useState("");

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files.length > 0) {
      setSelectedFile(event.target.files[0]);
      setMessage("");
    }
  };

  const handleSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    if (!selectedFile) {
      setMessage("Please select a file first.");
      return;
    }
    // Placeholder for backend upload logic
    setMessage(`Received file: ${selectedFile.name}`);
  };

  return (
    <main className="min-h-screen bg-black text-white flex flex-col items-center p-10">
      <h1 className="text-3xl font-bold text-green-500 mb-6">
        Upload Sustainability Report
      </h1>

      <form
        onSubmit={handleSubmit}
        className="bg-gray-900 p-8 rounded-lg shadow-md w-full max-w-md flex flex-col items-center space-y-6"
      >
        <input
          type="file"
          accept=".pdf,.docx,.xlsx"
          onChange={handleFileChange}
          className="w-full text-gray-200 cursor-pointer file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-green-700 file:text-white hover:file:bg-green-800"
        />

        <button
          type="submit"
          className="bg-green-600 hover:bg-green-700 text-white font-semibold py-2 px-6 rounded-lg transition duration-200"
        >
          Upload
        </button>
      </form>

      {message && <p className="mt-6 text-gray-300">{message}</p>}
    </main>
  );
}