import { Link, NavLink } from "react-router-dom";
import { Home } from "lucide-react";

export default function TopNav() {
  return (
    <div className="sticky top-0 z-40 border-b border-white/10 glass">
      <div className="max-w-6xl mx-auto px-4 h-14 flex items-center justify-between">
        <Link to="/" className="font-display text-lg">
          <span className="bg-gradient-to-r from-neon.pink via-neon.purple to-neon.blue bg-clip-text text-transparent font-semibold">
            AI Teaching Assistant
          </span>
        </Link>
        <nav className="flex gap-4 text-sm">
          <NavLink to="/" className="hover:text-white/90 flex items-center gap-1">
            <Home size={16}/> Home
          </NavLink>
          <NavLink to="/studyplan" className="hover:text-white/90">Study Plan</NavLink>
          <NavLink to="/worksheet" className="hover:text-white/90">Worksheet</NavLink>
          <NavLink to="/voice" className="hover:text-white/90">Voice</NavLink>
        </nav>
      </div>
    </div>
  );
}
