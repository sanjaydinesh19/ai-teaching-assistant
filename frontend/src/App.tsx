import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import TopNav from "./components/TopNav";
import Home from "./pages/Home";
import StudyPlan from "./pages/StudyPlan";
import Worksheet from "./pages/Worksheet";
import Voice from "./pages/Voice";

export default function App() {
  return (
    <BrowserRouter>
      <TopNav />
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/studyplan" element={<StudyPlan />} />
        <Route path="/worksheet" element={<Worksheet />} />
        <Route path="/voice" element={<Voice />} />
        <Route path="*" element={<Home />} />
      </Routes>
    </BrowserRouter>
  );
}
