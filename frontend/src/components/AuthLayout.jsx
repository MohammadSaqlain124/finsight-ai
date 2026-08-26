import styles from './AuthLayout.module.css'

function AuthLayout({ title, subtitle, footer, children }) {
  return (
    <div className={styles.shell}>
      <aside className={styles.brand}>
        <svg className={styles.veins} viewBox="0 0 600 1000" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <linearGradient id="veinGold" x1="0" y1="0" x2="1" y2="1">
              <stop offset="0" stopColor="#E8C989" />
              <stop offset="0.5" stopColor="#C9A15A" />
              <stop offset="1" stopColor="#8C6A2E" />
            </linearGradient>
          </defs>
          <g fill="none" stroke="url(#veinGold)" strokeLinecap="round">
            <path d="M-20 60 C 120 130, 90 250, 240 300 S 430 430, 520 560" strokeWidth="2.2" opacity="0.9" />
            <path d="M40 -10 C 90 120, 180 160, 210 320 S 300 520, 470 690" strokeWidth="1.4" opacity="0.7" />
            <path d="M-10 260 C 130 300, 160 430, 300 470 S 470 640, 560 760" strokeWidth="1.1" opacity="0.6" />
            <path d="M120 40 C 150 160, 60 230, 150 360 S 250 560, 360 900" strokeWidth="0.9" opacity="0.55" />
            <path d="M-20 520 C 120 560, 150 680, 280 720 S 430 860, 540 980" strokeWidth="1.6" opacity="0.65" />
            <path d="M240 120 C 300 220, 250 330, 360 420" strokeWidth="0.7" opacity="0.5" />
            <path d="M60 700 C 160 760, 180 850, 300 900" strokeWidth="0.8" opacity="0.5" />
          </g>
        </svg>

        <div className={styles.content}>
          <p className={styles.wordmark}>FinSight AI</p>
          <div>
            <p className={styles.tagline}>Your money,<br />in the black.</p>
            <div className={styles.ledger}>
              <p className={styles.ledgerHead}>Statement · August</p>
              <div className={styles.row}><span>Salary</span><span className={styles.amt}>+₹82,000.00</span></div>
              <div className={styles.row}><span>Groceries</span><span className={`${styles.amt} ${styles.amtNeg}`}>-₹6,240.00</span></div>
              <div className={styles.row}><span>Netflix</span><span className={`${styles.amt} ${styles.amtNeg}`}>-₹649.00</span></div>
              <div className={`${styles.row} ${styles.rowTotal}`}><span>Net</span><span className={styles.amt}>+₹75,111.00</span></div>
            </div>
          </div>
          <p className={styles.brandFoot}>AI-powered personal finance analysis</p>
        </div>
      </aside>

      <main className={styles.formCol}>
        <div className={styles.formInner}>
          <p className={styles.mobileBrand}>FinSight AI</p>
          <h1 className={styles.title}>{title}</h1>
          {subtitle && <p className={styles.subtitle}>{subtitle}</p>}
          {children}
          {footer && <p className={styles.footer}>{footer}</p>}
        </div>
      </main>
    </div>
  )
}

export default AuthLayout