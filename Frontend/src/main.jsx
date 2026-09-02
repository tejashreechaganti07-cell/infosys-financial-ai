import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App.jsx";
import "./index.css";
import { applyTheme, getInitialTheme } from "./hooks/useTheme";

try {
  applyTheme(getInitialTheme());
} catch (e) {
  console.error("Theme error:", e);
}

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);