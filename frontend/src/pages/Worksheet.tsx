import React, { useState } from "react";
import Upload from "../components/Upload";
import { generateWorksheet, API } from "../api";

export default function Worksheet() {
  const [fileId, setFileId] = useState("upload-img1");
  const [result, setResult] = useState<any>(null);

  const submit = async () => {
    const res = await generateWorksheet({
      file_id: fileId,
      grade_bands: ["3-4"],
      difficulty_curve: "easy-to-hard",
      question_mix: { mcq: 3, short: 2, diagram: 1 },
    });
    setResult(res);
  };

  return (
    <div>
      <h2>Worksheet</h2>
      <label>File ID: <input value={fileId} onChange={(e) => setFileId(e.target.value)} /></label>
      <Upload label="Upload Textbook Image (png/jpg)" fileId={fileId} />
      <button style={{ marginTop: 12 }} onClick={submit}>Generate Worksheet</button>

      {result && (
        <div style={{ marginTop: 16 }}>
          <h3>Items</h3>
          <ol>{result.items?.map((it: any, idx: number) => (
              <li key={idx}>{it.type}: {it.q}</li>
          ))}</ol>
          <a href={`${API}${result.printable_pdf_url}`} target="_blank" rel="noreferrer">
            Download PDF
          </a>
        </div>
      )}
    </div>
  );
}
