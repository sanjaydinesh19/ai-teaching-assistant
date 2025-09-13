import React, { useState } from "react";

const Voice: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [language, setLanguage] = useState("en");
  const [loading, setLoading] = useState(false);
  const [transcript, setTranscript] = useState("");
  const [audioUrl, setAudioUrl] = useState("");

  const handleUpload = async () => {
    if (!file) return;

    setLoading(true);
    setTranscript("");
    setAudioUrl("");

    try {
      // Step 1: Upload file
      const formData = new FormData();
      formData.append("file", file);
      formData.append("file_id", "upload-audio1");

      const uploadResp = await fetch("http://localhost:8000/upload", {
        method: "POST",
        body: formData,
      });

      if (!uploadResp.ok) throw new Error("Upload failed");
      const { file_id } = await uploadResp.json();

      // Step 2: Call voice-agent via gateway
      const resp = await fetch("http://localhost:8000/voice/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          file_id,
          target_language: language,
        }),
      });

      if (!resp.ok) throw new Error("Voice processing failed");
      const data = await resp.json();
      setTranscript(
        (data.transcript ? "Transcript:\n" + data.transcript + "\n\n" : "") +
        (data.answer_text ? "Answer:\n" + data.answer_text : "")
      );
      setAudioUrl(data.answer_audio_url ? `http://localhost:8000${data.answer_audio_url}` : "");

    } catch (err) {
      console.error(err);
      setTranscript("Error processing voice input.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">Voice Teaching Assistant</h1>

      <input
        type="file"
        accept="audio/*"
        onChange={(e) => setFile(e.target.files?.[0] || null)}
        className="mb-4"
      />

      <select
        value={language}
        onChange={(e) => setLanguage(e.target.value)}
        className="border p-2 rounded mb-4"
      >
        <option value="en">English</option>
        <option value="hi">Hindi</option>
        <option value="ta">Tamil</option>
      </select>
      
      <button
        onClick={handleUpload}
        disabled={loading || !file}
        className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 disabled:bg-gray-400"
      >
        {loading ? "Processing..." : "Upload & Generate"}
      </button>

      {transcript && (
        <div className="mt-6">
          <h2 className="text-lg font-semibold">Transcript:</h2>
          <p className="bg-gray-100 p-3 rounded">{transcript}</p>
        </div>
      )}

      {audioUrl && (
        <div className="mt-6">
          <h2 className="text-lg font-semibold">AI Audio Response:</h2>
          <audio controls src={audioUrl} className="mt-2 w-full" />
        </div>
      )}
    </div>
  );
};

export default Voice;
