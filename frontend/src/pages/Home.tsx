import { motion } from "framer-motion";
import NeonCard from "../components/NeonCard";
import { BookOpen, FileImage, Mic2 } from "lucide-react";

export default function Home() {
  return (
    <div className="min-h-screen">
      <main className="max-w-6xl mx-auto px-4 py-10">
        {/* Hero */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="text-center mb-10"
        >
          <h1 className="font-display text-4xl md:text-5xl leading-tight">
            Multimodal, Multilingual Assistant{" "}
            <span className="bg-gradient-to-r from-neon.pink via-neon.purple to-neon.blue bg-clip-text text-transparent">
              AI Assistant for Rural Teachers
            </span>
          </h1>
          <p className="text-white/75 mt-4 max-w-3xl mx-auto">
            We don’t just parse your syllabus — we give you localized, practical teaching
            support in your own language. Plan lessons, generate worksheets, and speak to
            an assistant that understands you.
          </p>
        </motion.div>

        {/* Floating blobs */}
        <motion.div
          className="pointer-events-none fixed -z-10 top-20 left-0 right-0 mx-auto w-[700px] h-[700px] rounded-full blur-3xl"
          animate={{ y: [0, -12, 0] }}
          transition={{ repeat: Infinity, duration: 12, ease: "easeInOut" }}
          style={{ background: "radial-gradient(closest-side, rgba(157,75,255,0.25), transparent)" }}
        />
        <motion.div
          className="pointer-events-none fixed -z-10 bottom-10 -right-10 w-[500px] h-[500px] rounded-full blur-3xl"
          animate={{ x: [0, 10, -10, 0] }}
          transition={{ repeat: Infinity, duration: 16, ease: "easeInOut" }}
          style={{ background: "radial-gradient(closest-side, rgba(75,234,255,0.2), transparent)" }}
        />

        {/* Feature grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
          <NeonCard
            to="/studyplan"
            icon={<BookOpen className="text-neon.purple" />}
            title="Study Plan"
            desc="Upload a syllabus PDF and get a localized, week-by-week plan with activities, assessments, and resources in your language."
          />
          <NeonCard
            to="/worksheet"
            icon={<FileImage className="text-neon.blue" />}
            title="Worksheet"
            desc="Turn PDFs, PPTs, and images into unique, difficulty-tiered worksheets; download print-ready PDFs for each set."
          />
          <NeonCard
            to="/voice"
            icon={<Mic2 className="text-neon.pink" />}
            title="Voice Assistant"
            desc="Record or upload audio, get transcripts and explanations, and listen to answers in Hindi, Tamil, or English."
          />
        </div>
      </main>
    </div>
  );
}
