import { ChartSettingsProvider } from "@/context/ChartSettingsContext.tsx";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App.tsx";
import "./index.css";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <ChartSettingsProvider>
      <App />
    </ChartSettingsProvider>
  </StrictMode>,
);
