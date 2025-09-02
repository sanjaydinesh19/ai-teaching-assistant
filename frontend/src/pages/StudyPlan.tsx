import React, { useState } from "react";
import Upload from "../components/Upload";
import Button from "../components/Button";
import Spinner from "../components/Spinner";
import Alert from "../components/Alert";
import { createStudyPlan } from "../api";

export default function StudyPlan() {
  const [fileId, setFileId] = useState("upload-123");
  const [grades, setGrades] = useState("3,4,5");
  const [weeks, setWeeks] = useState(8);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string | null>(null);
  const [result, setResult] = useState<any>(null);

  const submit = async () => {
    setErr(null);
    setResult(null);
    setLoading(true);
    try {
      const payload = {
        file_id: fileId,
        grades: grades.split(",").map((s) => s.trim()),
        duration_weeks: weeks,
        constraints: { per_day_minutes: 35, weekdays: ["Mon","Wed","Fri"] },
      };
      const res = await createStudyPlan(payload);
      setResult(res);
    } catch (e: any) {
      setErr(e.message || "Failed to generate study plan");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="grid gap-4">
      <div className="rounded-xl border bg-white p-4">
        <div className="grid gap-3 sm:grid-cols-3">
          <label className="text-sm">
            <div className="mb-1 font-medium">File ID</div>
            <input className="w-full rounded-lg border px-3 py-2" value={fileId} onChange={(e)=>setFileId(e.target.value)} />
          </label>
          <label className="text-sm">
            <div className="mb-1 font-medium">Grades (comma)</div>
            <input className="w-full rounded-lg border px-3 py-2" value={grades} onChange={(e)=>setGrades(e.target.value)} />
          </label>
          <label className="text-sm">
            <div className="mb-1 font-medium">Weeks</div>
            <input type="number" className="w-full rounded-lg border px-3 py-2" value={weeks} onChange={(e)=>setWeeks(Number(e.target.value))} />
          </label>
        </div>
        <div className="mt-3">
          <Upload label="Upload Syllabus PDF" fileId={fileId} accept="application/pdf" />
        </div>
        <div className="mt-3">
          <Button onClick={submit} loading={loading}>Generate Study Plan</Button>
        </div>
        {loading ? <div className="mt-3"><Spinner label="Generating Study Plan..." /></div> : null}
        {err ? <div className="mt-3"><Alert kind="error">{err}</Alert></div> : null}
      </div>

      {result && (
        <div className="rounded-xl border bg-white p-4">
          <h3 className="mb-2 text-lg font-semibold">Overview</h3>
          <p className="text-gray-800">{result.overview}</p>
          <h3 className="mb-2 mt-4 text-lg font-semibold">Weekly Outline</h3>
          <ol className="grid gap-2">
            {result.weekly_outline?.map((w: any) => (
              <li key={w.week} className="rounded-lg border p-3">
                <div className="font-medium">Week {w.week}</div>
                <div className="text-sm text-gray-700">{w.topics?.join(", ")}</div>
              </li>
            ))}
          </ol>
        </div>
      )}
    </div>
  );
}
