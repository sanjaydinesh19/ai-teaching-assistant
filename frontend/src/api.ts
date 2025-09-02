const API = process.env.REACT_APP_API || "http://localhost:8000";

export async function uploadFile(file: File, fileId: string) {
  const form = new FormData();
  form.append("file", file);
  form.append("file_id", fileId);
  const res = await fetch(`${API}/upload`, { method: "POST", body: form });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function createStudyPlan(payload: any) {
  const res = await fetch(`${API}/studyplan/from-syllabus`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function generateWorksheet(payload: any) {
  const res = await fetch(`${API}/image/worksheet`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function voiceAsk(payload: any) {
  const res = await fetch(`${API}/voice/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export { API };
