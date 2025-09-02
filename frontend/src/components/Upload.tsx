import React, { useState } from "react";
import { uploadFile } from "../api";

type Props = {
  label: string;
  fileId: string;
  onUploaded?: (savedAs: string) => void;
};

export default function Upload({ label, fileId, onUploaded }: Props) {
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState<string>("");

  const doUpload = async () => {
    if (!file) return;
    setStatus("Uploading...");
    try {
      const res = await uploadFile(file, fileId);
      setStatus(`Uploaded as ${res.saved_as}`);
      onUploaded?.(res.saved_as);
    } catch (e: any) {
      setStatus(`Error: ${e.message}`);
    }
  };

  return (
    <div style={{ border: "1px solid #ddd", padding: 12, borderRadius: 8 }}>
      <div style={{ marginBottom: 8, fontWeight: 600 }}>{label}</div>
      <input type="file" onChange={(e) => setFile(e.target.files?.[0] || null)} />
      <button onClick={doUpload} style={{ marginLeft: 8 }}>Upload</button>
      <div style={{ marginTop: 6, fontSize: 12, color: "#666" }}>{status}</div>
    </div>
  );
}
