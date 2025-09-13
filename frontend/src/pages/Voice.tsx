import React, { useState } from "react";

const Voice: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [language, setLanguage] = useState("en");
  const [loading, setLoading] = useState(false);
  const [transcript, setTranscript] = useState("");
  const [answer, setAnswer] = useState("");
  const [audioUrl, setAudioUrl] = useState("");

  const handleUpload = async () => {
    if (!file) return;

    setLoading(true);
    setTranscript("");
    setAnswer("");
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
      setTranscript(data.transcript || "");   // always update from backend
      setAnswer(data.answer_text || "");
      setAudioUrl(data.answer_audio_url ? `http://localhost:8000${data.answer_audio_url}` : "");


    } catch (err) {
      console.error(err);
      setTranscript("Error processing voice input.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 max-w-2xl mx-auto text-gray-200">
      <h1 className="text-2xl font-bold mb-4 text-white">Voice Teaching Assistant</h1>

      <input
        type="file"
        accept="audio/*"
        onChange={(e) => setFile(e.target.files?.[0] || null)}
        className="bg-[#1a1a25] border border-purple-500 rounded p-2 w-full text-white mb-4"
      />

      <select
        value={language}
        onChange={(e) => setLanguage(e.target.value)}
        className="bg-[#1a1a25] border border-purple-500 rounded p-2 w-full text-white mb-6"
      >
        <option value="en">English</option>
        <option value="hi">Hindi</option>
        <option value="ta">Tamil</option>
      </select>
      
      <button
        onClick={handleUpload}
        disabled={loading || !file}
        className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded shadow-lg disabled:opacity-50 transition w-full"
      >
        {loading ? "Processing..." : "Upload & Generate"}
      </button>

      {transcript && (
        <div className="mt-6">
          <h2 className="text-lg font-semibold text-white">Transcript:</h2>
          <p className="bg-[#1a1a25] border border-purple-500 p-3 rounded text-white whitespace-pre-line">
            {transcript}
          </p>
        </div>
      )}

      {answer && (
        <div className="mt-6">
          <h2 className="text-lg font-semibold text-white">AI Answer:</h2>
          <p className="bg-[#1a1a25] border border-purple-500 p-3 rounded text-white whitespace-pre-line">
            {answer}
          </p>
        </div>
      )}


      {audioUrl && (
        <div className="mt-6">
          <h2 className="text-lg font-semibold text-white">AI Audio Response:</h2>
          <audio controls src={audioUrl} className="mt-2 w-full" />
        </div>
      )}
    </div>
  );
};

export default Voice;
