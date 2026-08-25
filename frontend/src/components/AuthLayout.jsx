import styles from './AuthLayout.module.css'

function AuthLayout({ title, subtitle, footer, children }) {
  return (
    <div className={styles.shell}>
      <aside className={styles.brand}>
        <p className={styles.wordmark}>FinSight AI</p>

        <div>
          <p className={styles.tagline}>Your money,<br />in the black.</p>

          <div className={styles.ledger}>
            <p className={styles.ledgerHead}>Statement · August</p>
            <div className={styles.row}>
              <span>Salary</span>
              <span className={styles.amt}>+₹82,000.00</span>
            </div>
            <div className={styles.row}>
              <span>Groceries</span>
              <span className={`${styles.amt} ${styles.amtNeg}`}>-₹6,240.00</span>
            </div>
            <div className={styles.row}>
              <span>Netflix</span>
              <span className={`${styles.amt} ${styles.amtNeg}`}>-₹649.00</span>
            </div>
            <div className={`${styles.row} ${styles.rowTotal}`}>
              <span>Net</span>
              <span className={styles.amt}>+₹75,111.00</span>
            </div>
          </div>
        </div>

        <p className={styles.brandFoot}>AI-powered personal finance analysis</p>
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