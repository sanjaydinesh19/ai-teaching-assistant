import React, { useState } from "react";
import Upload from "../components/Upload";
import { createStudyPlan, API } from "../api";

export default function StudyPlan() {
  const [fileId, setFileId] = useState("upload-123");
  const [grades, setGrades] = useState("3,4,5");
  const [weeks, setWeeks] = useState(8);
  const [result, setResult] = useState<any>(null);

  const submit = async () => {
    const payload = {
      file_id: fileId,
      grades: grades.split(",").map((s) => s.trim()),
      duration_weeks: weeks,
      constraints: { per_day_minutes: 35, weekdays: ["Mon","Wed","Fri"] }
    };
    const res = await createStudyPlan(payload);
    setResult(res);
  };

  return (
    <div>
      <h2>Study Plan</h2>
      <label>File ID: <input value={fileId} onChange={(e) => setFileId(e.target.value)} /></label>
      <Upload label="Upload Syllabus PDF" fileId={fileId} />
      <div style={{ marginTop: 8 }}>
        <label>Grades (comma): <input value={grades} onChange={(e)=>setGrades(e.target.value)} /></label>
      </div>
      <div style={{ marginTop: 8 }}>
        <label>Weeks: <input type="number" value={weeks} onChange={(e)=>setWeeks(Number(e.target.value))} /></label>
      </div>
      <button style={{ marginTop: 12 }} onClick={submit}>Generate Plan</button>

      {result && (
        <div style={{ marginTop: 16 }}>
          <h3>Overview</h3>
          <p>{result.overview}</p>
          <h3>Weekly Outline</h3>
          <ol>
            {result.weekly_outline?.map((w: any) => (
              <li key={w.week}><b>Week {w.week}</b>: {w.topics?.join(", ")}</li>
            ))}
          </ol>
        </div>
      )}
    </div>
  );
}
