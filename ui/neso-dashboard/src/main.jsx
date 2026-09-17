import React from "react";
import { createRoot } from "react-dom/client";

function App() {
  return (
    <main style={{ fontFamily: "Arial", padding: 32 }}>
      <h1>NESO Strategy & Policy</h1>
      <h2>Emissions Counting</h2>
      <p>Dashboard starter. Connect this UI to the FastAPI output contract.</p>
      <button>Start Model Run</button>
    </main>
  );
}

createRoot(document.getElementById("root")).render(<App />);
