import React, { useState } from "react";
import Upload from "../components/Upload";
import Button from "../components/Button";
import Spinner from "../components/Spinner";
import Alert from "../components/Alert";
import { voiceAsk, API } from "../api";

export default function Voice() {
  const [fileId, setFileId] = useState("upload-audio1");
  const [level, setLevel] = useState("grade-5");
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  const [result, setResult] = useState<any>(null);

  const submit = async () => {
    setErr(null); setResult(null); setLoading(true);
    try {
      const res = await voiceAsk({
        audio_file_id: fileId,
        level,
        visual_format: "board-notes",
        max_seconds: 60
      });
      setResult(res);
    } catch (e: any) {
      setErr(e.message || "Failed to process audio");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="grid gap-4">
      <div className="rounded-xl border bg-white p-4">
        <div className="grid gap-3 sm:grid-cols-2">
          <label className="text-sm">
            <div className="mb-1 font-medium">File ID</div>
            <input className="w-full rounded-lg border px-3 py-2" value={fileId} onChange={(e)=>setFileId(e.target.value)} />
          </label>
          <label className="text-sm">
            <div className="mb-1 font-medium">Level</div>
            <input className="w-full rounded-lg border px-3 py-2" value={level} onChange={(e)=>setLevel(e.target.value)} />
          </label>
        </div>
        <div className="mt-3">
          <Upload label="Upload Audio (wav/mp3)" fileId={fileId} accept="audio/*" />
        </div>
        <div className="mt-3">
          <Button onClick={submit} loading={loading}>Ask</Button>
        </div>
        {loading ? <div className="mt-3"><Spinner label="Processing Audio..." /></div> : null}
        {err ? <div className="mt-3"><Alert kind="error">{err}</Alert></div> : null}
      </div>

      {result && (
        <div className="rounded-xl border bg-white p-4">
          <h3 className="mb-2 text-lg font-semibold">Transcript</h3>
          <p className="text-gray-800">{result.transcript}</p>
          <h3 className="mb-2 mt-4 text-lg font-semibold">Explanation</h3>
          <p className="text-gray-800 whitespace-pre-wrap">{result.explanation}</p>
          <audio className="mt-4 w-full" controls src={`${API}${result.audio_url}`} />
        </div>
      )}
    </div>
  );
}
