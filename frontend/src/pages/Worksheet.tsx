import React, { useEffect, useMemo, useState } from "react";

type Difficulty = "easy" | "medium" | "hard";

type WorksheetSet = {
  set_no: number;
  difficulty: Difficulty;
  printable_pdf_url: string;
  items: Array<{
    type: string;
    q: string;
    options?: string[];
    answer?: string;
    rubric?: string;
  }>;
};

type WorksheetResponse = {
  worksheet_id: string;
  sets: WorksheetSet[];
};

const API_BASE = "http://localhost:8000";

const DIFFS: Difficulty[] = ["easy", "medium", "hard"];

export default function Worksheet() {
  const [files, setFiles] = useState<File[]>([]);
  const [gradeBands, setGradeBands] = useState<string>("3-4");
  const [language, setLanguage] = useState<string>("en");
  const [numSets, setNumSets] = useState<number>(3);
  const [mode, setMode] = useState<"broadcast" | "per-set">("per-set");
  const [broadcastDiff, setBroadcastDiff] = useState<Difficulty>("easy");
  const [perSetDiffs, setPerSetDiffs] = useState<Difficulty[]>(["easy", "medium", "hard"]);
  const [questionsPerSet, setQuestionsPerSet] = useState<number>(6);
  const [mixMcq, setMixMcq] = useState<number>(3);
  const [mixShort, setMixShort] = useState<number>(2);
  const [mixDiagram, setMixDiagram] = useState<number>(1);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<WorksheetResponse | null>(null);

  // keep per-set difficulty length in sync with numSets
  useEffect(() => {
    setPerSetDiffs(prev => {
      const copy = prev.slice(0, numSets);
      while (copy.length < numSets) copy.push("easy");
      return copy;
    });
  }, [numSets]);

  const difficultyLevels: Difficulty[] = useMemo(() => {
    if (mode === "broadcast") return Array(numSets).fill(broadcastDiff);
    return perSetDiffs.slice(0, numSets);
  }, [mode, numSets, broadcastDiff, perSetDiffs]);

  const onFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = Array.from(e.target.files || []);
    setFiles(f);
  };

  const parseGradeBands = (val: string): string[] => {
    return val
      .split(",")
      .map(s => s.trim())
      .filter(Boolean);
  };

  const generateIdFor = (f: File) => {
    const base = f.name.replace(/\.[^/.]+$/, "");
    const safe = base.toLowerCase().replace(/[^a-z0-9\-]+/g, "-").slice(0, 40);
    return `upload-${Date.now()}-${safe}`;
  };

  const uploadOne = async (file: File, file_id: string) => {
    const form = new FormData();
    form.append("file_id", file_id);
    form.append("file", file);
    const r = await fetch(`${API_BASE}/upload`, { method: "POST", body: form });
    if (!r.ok) throw new Error(`Upload failed for ${file.name}: ${await r.text()}`);
    return file_id;
  };

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!files.length) {
      setError("Please choose at least one file (PDF/PPT/PPTX/PNG/JPG).");
      return;
    }
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      // 1) Upload each file and collect file_ids (no extension)
      const fileIds: string[] = [];
      for (const f of files) {
        const id = generateIdFor(f);
        await uploadOne(f, id);
        fileIds.push(id);
      }

      // 2) Build question mix
      const mix: Record<string, number> = {};
      if (mixMcq > 0) mix["mcq"] = mixMcq;
      if (mixShort > 0) mix["short"] = mixShort;
      if (mixDiagram > 0) mix["diagram"] = mixDiagram;

      // 3) Build payload
      const payload = {
        file_ids: fileIds,
        grade_bands: parseGradeBands(gradeBands),
        num_sets: numSets,
        difficulty_levels: difficultyLevels,
        questions_per_set: questionsPerSet,
        question_mix: mix,
        target_language: language
      };

      // 4) Call worksheet generator
      const r = await fetch(`${API_BASE}/image/worksheet`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      if (!r.ok) throw new Error(await r.text());
      const data: WorksheetResponse = await r.json();
      setResult(data);
    } catch (err: any) {
      setError(err.message || String(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-6 max-w-3xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">Worksheet Generator</h1>

      <form onSubmit={onSubmit} className="space-y-5">
        <div>
          <label className="block mb-1 font-medium">Upload Files (multiple)</label>
          <input
            type="file"
            multiple
            accept=".pdf,.ppt,.pptx,.png,.jpg,.jpeg"
            onChange={onFileChange}
            className="border rounded p-2 w-full"
          />
          {files.length > 0 && (
            <p className="text-sm text-gray-600 mt-1">
              Selected: {files.map(f => f.name).join(", ")}
            </p>
          )}
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block mb-1 font-medium">Grade Bands</label>
            <input
              type="text"
              value={gradeBands}
              onChange={e => setGradeBands(e.target.value)}
              placeholder="e.g. 3-4 or 5,6"
              className="border rounded p-2 w-full"
            />
          </div>

          <div>
            <label className="block mb-1 font-medium">Language</label>
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
            <label className="block mb-1 font-medium">Questions per set</label>
            <input
              type="number"
              min={2}
              max={50}
              value={questionsPerSet}
              onChange={e => setQuestionsPerSet(Number(e.target.value))}
              className="border rounded p-2 w-full"
            />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block mb-1 font-medium">Number of Sets</label>
            <input
              type="number"
              min={1}
              max={10}
              value={numSets}
              onChange={e => setNumSets(Number(e.target.value))}
              className="border rounded p-2 w-full"
            />
          </div>

          <div>
            <label className="block mb-1 font-medium">Difficulty Mode</label>
            <select
              value={mode}
              onChange={e => setMode(e.target.value as "broadcast" | "per-set")}
              className="border rounded p-2 w-full"
            >
              <option value="per-set">Per set (choose for each)</option>
              <option value="broadcast">Same difficulty for all</option>
            </select>
          </div>

          {mode === "broadcast" && (
            <div>
              <label className="block mb-1 font-medium">Broadcast Difficulty</label>
              <select
                value={broadcastDiff}
                onChange={e => setBroadcastDiff(e.target.value as Difficulty)}
                className="border rounded p-2 w-full"
              >
                {DIFFS.map(d => (
                  <option key={d} value={d}>{d}</option>
                ))}
              </select>
            </div>
          )}
        </div>

        {mode === "per-set" && (
          <div className="border rounded p-3">
            <p className="font-medium mb-2">Difficulty per Set</p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              {Array.from({ length: numSets }).map((_, idx) => (
                <div key={idx} className="flex items-center gap-2">
                  <span className="text-sm text-gray-700 w-20">Set {idx + 1}</span>
                  <select
                    value={perSetDiffs[idx] || "easy"}
                    onChange={e => {
                      const next = [...perSetDiffs];
                      next[idx] = e.target.value as Difficulty;
                      setPerSetDiffs(next);
                    }}
                    className="border rounded p-2 flex-1"
                  >
                    {DIFFS.map(d => (
                      <option key={d} value={d}>{d}</option>
                    ))}
                  </select>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="border rounded p-3">
          <p className="font-medium mb-2">Question Mix (optional)</p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            <label className="flex items-center gap-2">
              <span className="w-20">MCQ</span>
              <input type="number" min={0} value={mixMcq} onChange={e => setMixMcq(Number(e.target.value))} className="border rounded p-2 w-24" />
            </label>
            <label className="flex items-center gap-2">
              <span className="w-20">Short</span>
              <input type="number" min={0} value={mixShort} onChange={e => setMixShort(Number(e.target.value))} className="border rounded p-2 w-24" />
            </label>
            <label className="flex items-center gap-2">
              <span className="w-20">Diagram</span>
              <input type="number" min={0} value={mixDiagram} onChange={e => setMixDiagram(Number(e.target.value))} className="border rounded p-2 w-24" />
            </label>
          </div>
          <p className="text-xs text-gray-500 mt-2">
            Leave zeros if you don’t want that type; otherwise the model will follow this distribution as closely as possible.
          </p>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="bg-blue-600 text-white px-4 py-2 rounded disabled:opacity-50"
        >
          {loading ? "Generating…" : "Generate Worksheets"}
        </button>
      </form>

      {error && <p className="text-red-600 mt-4">{error}</p>}

      {result && (
        <div className="mt-6 p-4 border rounded bg-gray-50">
          <h2 className="text-lg font-semibold mb-2">Generated Sets</h2>
          <ul className="space-y-2">
            {result.sets.map(s => (
              <li key={s.set_no} className="flex items-center justify-between bg-white border rounded p-2">
                <div>
                  <div className="font-medium">Set {s.set_no} — {s.difficulty}</div>
                </div>
                <a
                  href={`${API_BASE}${s.printable_pdf_url}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 underline"
                >
                  Download {s.printable_pdf_url.split("/").pop()}
                </a>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
