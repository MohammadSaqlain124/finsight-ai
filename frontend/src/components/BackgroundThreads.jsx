// Faint wavy gold/green/red threads for the paper background.
// Render it as the first child of a position:relative page container.
function BackgroundThreads() {
  return (
    <svg
      aria-hidden="true"
      viewBox="0 0 1440 900"
      preserveAspectRatio="none"
      style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', zIndex: 0, pointerEvents: 'none' }}
      xmlns="http://www.w3.org/2000/svg"
    >
      <g fill="none" strokeLinecap="round">
        <path d="M-60 130 C 320 40, 520 250, 820 150 S 1240 60, 1520 190" stroke="#C9A15A" strokeWidth="1.4" opacity="0.32" />
        <path d="M-60 250 C 360 170, 640 320, 980 220 S 1300 150, 1520 270" stroke="#7E2E2E" strokeWidth="1.2" opacity="0.16" />
        <path d="M-60 350 C 300 300, 560 440, 900 350 S 1260 290, 1520 380" stroke="#2E4A3E" strokeWidth="1.2" opacity="0.16" />
        <path d="M-60 500 C 340 430, 620 600, 960 500 S 1280 440, 1520 540" stroke="#C9A15A" strokeWidth="1" opacity="0.26" />
        <path d="M-60 620 C 260 560, 600 720, 940 630 S 1240 560, 1520 650" stroke="#7E2E2E" strokeWidth="1" opacity="0.14" />
        <path d="M-60 760 C 320 700, 560 860, 900 770 S 1260 700, 1520 800" stroke="#2E4A3E" strokeWidth="1.2" opacity="0.15" />
        <path d="M-60 60 C 240 20, 460 120, 720 70 S 1160 20, 1520 90" stroke="#C9A15A" strokeWidth="0.8" opacity="0.22" />
        <path d="M-60 440 C 300 400, 520 520, 840 450 S 1220 400, 1520 470" stroke="#8C6A2E" strokeWidth="0.8" opacity="0.2" />
      </g>
    </svg>
  )
}

export default BackgroundThreads