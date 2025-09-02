import React, { useState } from "react";
import Upload from "../components/Upload";
import Button from "../components/Button";
import Spinner from "../components/Spinner";
import Alert from "../components/Alert";
import { generateWorksheet, API } from "../api";

export default function Worksheet() {
  const [fileId, setFileId] = useState("upload-img1");
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  const [result, setResult] = useState<any>(null);

  const submit = async () => {
    setErr(null); setResult(null); setLoading(true);
    try {
      const res = await generateWorksheet({
        file_id: fileId,
        grade_bands: ["3-4"],
        difficulty_curve: "easy-to-hard",
        question_mix: { mcq: 3, short: 2, diagram: 1 },
      });
      setResult(res);
    } catch (e: any) {
      setErr(e.message || "Failed to generate worksheet");
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
        </div>
        <div className="mt-3">
          <Upload label="Upload Textbook Image" fileId={fileId} accept="image/*" />
        </div>
        <div className="mt-3">
          <Button onClick={submit} loading={loading}>Generate Worksheet</Button>
        </div>
        {loading ? <div className="mt-3"><Spinner label="Generating Worksheet..." /></div> : null}
        {err ? <div className="mt-3"><Alert kind="error">{err}</Alert></div> : null}
      </div>

      {result && (
        <div className="rounded-xl border bg-white p-4">
          <h3 className="mb-3 text-lg font-semibold">Items</h3>
          <ol className="grid gap-3">
            {result.items?.map((it: any, idx: number) => (
              <li key={idx} className="rounded-lg border p-3">
                <div className="text-sm text-gray-500">{it.type.toUpperCase()}</div>
                <div className="font-medium">{it.q}</div>
                {it.options?.length ? (
                  <ul className="mt-2 list-disc pl-5 text-sm">
                    {it.options.map((o: string, i: number) => <li key={i}>{o}</li>)}
                  </ul>
                ) : null}
              </li>
            ))}
          </ol>
          <a
            className="mt-4 inline-block rounded-lg bg-green-600 px-4 py-2 text-white"
            href={`${API}${result.printable_pdf_url}`} target="_blank" rel="noreferrer"
          >
            Download PDF
          </a>
        </div>
      )}
    </div>
  );
}
