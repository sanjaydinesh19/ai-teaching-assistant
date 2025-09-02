import React from "react";
import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import StudyPlan from "./pages/StudyPlan";
import Worksheet from "./pages/Worksheet";
import Voice from "./pages/Voice";

export default function App() {
  return (
    <BrowserRouter>
      <div style={{ padding: 16 }}>
        <h1>AI Teaching Assistant</h1>
        <nav style={{ display: "flex", gap: 12 }}>
          <Link to="/">Study Plan</Link>
          <Link to="/worksheet">Worksheet</Link>
          <Link to="/voice">Voice</Link>
        </nav>
        <div style={{ marginTop: 16 }}>
          <Routes>
            <Route path="/" element={<StudyPlan />} />
            <Route path="/worksheet" element={<Worksheet />} />
            <Route path="/voice" element={<Voice />} />
          </Routes>
        </div>
      </div>
    </BrowserRouter>
  );
}
