import React from "react";
import { Link, useLocation } from "react-router-dom";

const NavLink = ({ to, children }: { to: string; children: React.ReactNode }) => {
  const { pathname } = useLocation();
  const active = pathname === to;
  return (
    <Link
      to={to}
      className={`px-3 py-2 rounded-lg text-sm font-medium ${
        active ? "bg-blue-600 text-white" : "text-blue-700 hover:bg-blue-50"
      }`}
    >
      {children}
    </Link>
  );
};

export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="border-b bg-white">
        <div className="mx-auto max-w-5xl px-4 py-4 flex items-center justify-between">
          <h1 className="text-xl font-semibold">AI Teaching Assistant</h1>
          <nav className="flex gap-2">
            <NavLink to="/">Study Plan</NavLink>
            <NavLink to="/worksheet">Worksheet</NavLink>
            <NavLink to="/voice">Voice</NavLink>
          </nav>
        </div>
      </header>
      <main className="mx-auto max-w-5xl px-4 py-6">{children}</main>
    </div>
  );
}
