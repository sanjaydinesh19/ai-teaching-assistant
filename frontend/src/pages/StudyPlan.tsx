import React, { useState } from "react";

export default function StudyPlan() {
  const [file, setFile] = useState<File | null>(null);
  const [grades, setGrades] = useState<string>("4");
  const [language, setLanguage] = useState<string>("en");
  const [weeks, setWeeks] = useState<number>(8);
  const [minutes, setMinutes] = useState<number>(35);
  const [weekdays, setWeekdays] = useState<string[]>(["Mon","Wed","Fri"]);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleCheckbox = (day: string) => {
    setWeekdays(prev =>
      prev.includes(day) ? prev.filter(d => d !== day) : [...prev, day]
    );
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return setError("Please upload a syllabus PDF");

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      // 1. Upload file
      const formData = new FormData();
      const fileId = `upload-${Date.now()}`;
      formData.append("file_id", fileId);
      formData.append("file", file);

      await fetch("http://localhost:8000/upload", {
        method: "POST",
        body: formData
      });

      // 2. Call studyplan
      const payload = {
        file_id: fileId,
        grades: grades.split(",").map(g => g.trim()),
        duration_weeks: weeks,
        constraints: { per_day_minutes: minutes, weekdays },
        target_language: language
      };

      const res = await fetch("http://localhost:8000/studyplan/from-syllabus", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      if (!res.ok) throw new Error(await res.text());
      const data = await res.json();
      setResult(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">Generate Study Plan</h1>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block mb-1">Upload Syllabus (PDF)</label>
          <input
            type="file"
            accept=".pdf"
            onChange={e => setFile(e.target.files?.[0] || null)}
            className="border rounded p-2 w-full"
          />
        </div>

        <div>
          <label className="block mb-1">Grades (comma separated)</label>
          <input
            type="text"
            value={grades}
            onChange={e => setGrades(e.target.value)}
            className="border rounded p-2 w-full"
            placeholder="e.g. 3,4,5"
          />
        </div>

        <div>
          <label className="block mb-1">Target Language</label>
          <select
            value={language}
            onChange={e => setLanguage(e.target.value)}
            className="border rounded p-2 w-full"
          >
            <option value="en">English</option>
            <option value="hi">Hindi</option>
            <option value="ta">Tamil</option>
          </select>
        </div>

        <div>
          <label className="block mb-1">Duration (weeks)</label>
          <input
            type="number"
            value={weeks}
            onChange={e => setWeeks(Number(e.target.value))}
            className="border rounded p-2 w-full"
          />
        </div>

        <div>
          <label className="block mb-1">Minutes per Class</label>
          <input
            type="number"
            value={minutes}
            onChange={e => setMinutes(Number(e.target.value))}
            className="border rounded p-2 w-full"
          />
        </div>

        <div>
          <label className="block mb-1">Class Days</label>
          <div className="flex gap-3 flex-wrap">
            {["Mon","Tue","Wed","Thu","Fri","Sat","Sun"].map(day => (
              <label key={day} className="flex items-center space-x-1">
                <input
                  type="checkbox"
                  checked={weekdays.includes(day)}
                  onChange={() => handleCheckbox(day)}
                />
                <span>{day}</span>
              </label>
            ))}
          </div>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="bg-blue-600 text-white px-4 py-2 rounded disabled:opacity-50"
        >
          {loading ? "Generating..." : "Generate"}
        </button>
      </form>

      {error && <p className="text-red-600 mt-4">{error}</p>}

      {result && (
        <div className="mt-6 p-4 border rounded bg-gray-50">
          <h2 className="text-lg font-semibold mb-2">Study Plan Generated ✅</h2>
          <p><strong>Grades:</strong> {result.grades.join(", ")}</p>
          <p><strong>Weeks:</strong> {result.weeks}</p>
          <p><strong>Language:</strong> {result.target_language}</p>
          <a
            href={`http://localhost:8000${result.printable_file_url}`}
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-600 underline"
          >
            Download {result.printable_file_url.split("/").pop()}
          </a>
        </div>
      )}
    </div>
  );
}
