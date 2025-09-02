import React from "react";
import { Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";
import StudyPlan from "./pages/StudyPlan";
import Worksheet from "./pages/Worksheet";
import Voice from "./pages/Voice";

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<StudyPlan />} />
        <Route path="/worksheet" element={<Worksheet />} />
        <Route path="/voice" element={<Voice />} />
      </Routes>
    </Layout>
  );
}
