import React from "react";
import { createRoot } from "react-dom/client";

function App() {
  return (
    <main style={{ fontFamily: "Arial, sans-serif", padding: 32 }}>
      <h1>NESO Emissions Counting</h1>
      <p>UI starter — connect this screen to the FastAPI output contract.</p>

      <section>
        <h2>Model Run</h2>
        <p>Status: Awaiting API integration</p>
        <button>Run Emissions Counting</button>
      </section>
    </main>
  );
}

createRoot(document.getElementById("root")).render(<App />);
