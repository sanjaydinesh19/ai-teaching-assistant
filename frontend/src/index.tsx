import React from "react";
import { createRoot } from "react-dom/client";
import App from "./App";
import "./index.css";

const el = document.getElementById("root");
if (!el) throw new Error("Missing #root element in index.html");

createRoot(el).render(
  <React.StrictMode>
      <App />
  </React.StrictMode>
);
