function App() {
  return (
    <main style={{ padding: "4rem", maxWidth: "640px" }}>
      <p style={{ color: "var(--ink-soft)", textTransform: "uppercase", letterSpacing: "0.15em", fontSize: "var(--text-sm)" }}>
        FinSight AI
      </p>
      <h1 style={{ fontSize: "var(--text-3xl)", marginTop: "0.5rem" }}>
        Your money, in the black.
      </h1>

      <div style={{ borderTop: "1px solid var(--rule)", marginTop: "2.5rem", paddingTop: "1.5rem" }}>
        <p style={{ color: "var(--ink-soft)", fontSize: "var(--text-sm)" }}>Net balance</p>
        <p className="figure" style={{ fontSize: "var(--text-2xl)" }}>₹1,24,750.00</p>
      </div>

      <div style={{ borderTop: "1px solid var(--rule)", marginTop: "1.5rem", paddingTop: "1.5rem" }}>
        <p style={{ color: "var(--ink-soft)", fontSize: "var(--text-sm)" }}>Biggest expense</p>
        <p className="figure figure--negative" style={{ fontSize: "var(--text-xl)" }}>-₹75,000.00</p>
      </div>
    </main>
  );
}

export default App;