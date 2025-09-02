import React, { useState } from "react";
import { uploadFile } from "../api";
import Alert from "./Alert";
import Button from "./Button";

type Props = {
  label: string;
  fileId: string;                 // no extension, e.g., "upload-123"
  accept?: string;                // e.g., "application/pdf,image/*,audio/*"
  onUploaded?: (savedAs: string) => void;
};

export default function Upload({ label, fileId, accept, onUploaded }: Props) {
  const [file, setFile] = useState<File | null>(null);
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState<{ kind: "info" | "success" | "error"; text: string } | null>(null);

  const doUpload = async () => {
    if (!file) return;
    setBusy(true);
    setMsg({ kind: "info", text: "Uploading..." });
    try {
      const res = await uploadFile(file, fileId);
      setMsg({ kind: "success", text: `Uploaded: ${res.saved_as}` });
      onUploaded?.(res.saved_as);
    } catch (e: any) {
      setMsg({ kind: "error", text: `Upload failed: ${e.message || "Unknown error"}` });
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="rounded-xl border bg-white p-4">
      <div className="mb-2 text-sm font-medium">{label}</div>
      <div className="flex items-center gap-2">
        <input
          type="file"
          accept={accept}
          onChange={(e) => setFile(e.target.files?.[0] || null)}
          className="block w-full text-sm"
        />
        <Button onClick={doUpload} loading={busy}>Upload</Button>
      </div>
      {msg ? <div className="mt-2"><Alert kind={msg.kind}>{msg.text}</Alert></div> : null}
    </div>
  );
}
