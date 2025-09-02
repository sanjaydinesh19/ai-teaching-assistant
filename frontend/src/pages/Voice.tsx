import React, { useState } from "react";
import Upload from "../components/Upload";
import { voiceAsk, API } from "../api";

export default function Voice() {
  const [fileId, setFileId] = useState("upload-audio1");
  const [level, setLevel] = useState("grade-5");
  const [result, setResult] = useState<any>(null);

  const submit = async () => {
    const res = await voiceAsk({
      audio_file_id: fileId,
      level,
      visual_format: "board-notes",
      max_seconds: 60
    });
    setResult(res);
  };

  return (
    <div>
      <h2>Voice Q&A</h2>
      <label>File ID: <input value={fileId} onChange={(e)=>setFileId(e.target.value)} /></label>
      <Upload label="Upload Audio (wav/mp3)" fileId={fileId} />
      <div style={{ marginTop: 8 }}>
        <label>Level: <input value={level} onChange={(e)=>setLevel(e.target.value)} /></label>
      </div>
      <button style={{ marginTop: 12 }} onClick={submit}>Ask</button>

      {result && (
        <div style={{ marginTop: 16 }}>
          <h3>Transcript</h3>
          <p>{result.transcript}</p>
          <h3>Explanation</h3>
          <p>{result.explanation}</p>
          <audio controls src={`${API}${result.audio_url}`} style={{ marginTop: 8 }} />
        </div>
      )}
    </div>
  );
}
