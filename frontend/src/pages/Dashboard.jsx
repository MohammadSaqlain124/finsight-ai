import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { apiFetch } from '../lib/api'
import { formatINR } from '../lib/format'
import Button from '../components/Button'
import styles from './Dashboard.module.css'

function Dashboard() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [summary, setSummary] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    apiFetch('/api/analytics/summary')
      .then(setSummary)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [])

  function handleLogout() {
    logout()
    navigate('/login')
  }

  const hasData = summary && summary.transaction_count > 0

  return (
    <div className={styles.page}>
      <header className={styles.topbar}>
        <div>
          <p className={styles.wordmark}>FinSight AI</p>
          <p className={styles.greeting}>
            {user ? `Welcome back, ${user.full_name}` : 'Welcome back'}
          </p>
        </div>
        <Button variant="secondary" onClick={handleLogout}>Sign out</Button>
      </header>

      <main className={styles.main}>
        {loading && <p className={styles.muted}>Loading your overview…</p>}

        {!loading && error && (
          <p className={styles.error}>Couldn’t load your summary: {error}</p>
        )}

        {!loading && !error && !hasData && (
          <div className={styles.empty}>
            <h1 className={styles.emptyTitle}>No transactions yet</h1>
            <p className={styles.muted} style={{ marginBottom: '1.5rem' }}>
              Upload a bank statement and FinSight will categorize and analyze it here.
            </p>
            <Button variant="primary" onClick={() => navigate('/upload')}>Upload a statement</Button>
          </div>
        )}

        {!loading && !error && hasData && (
          <>
            <section className={styles.hero}>
              <p className={styles.heroLabel}>Net savings</p>
              <p className={`figure ${styles.heroFigure} ${summary.net_savings < 0 ? 'figure--negative' : ''}`}>
                {summary.net_savings >= 0 ? '+' : ''}{formatINR(summary.net_savings)}
              </p>
              <p className={styles.muted}>
                You kept {summary.savings_rate}% of your income across {summary.transaction_count} transactions.
              </p>
            </section>

            <section className={styles.metrics}>
              <div className={styles.card}>
                <p className={styles.cardLabel}>Income</p>
                <p className={`figure ${styles.cardFigure}`}>{formatINR(summary.total_income)}</p>
              </div>
              <div className={styles.card}>
                <p className={styles.cardLabel}>Expenses</p>
                <p className={`figure figure--negative ${styles.cardFigure}`}>{formatINR(-summary.total_expenses)}</p>
              </div>
              <div className={styles.card}>
                <p className={styles.cardLabel}>Savings rate</p>
                <p className={`figure ${styles.cardFigure}`}>{summary.savings_rate}%</p>
              </div>
            </section>
          </>
        )}
      </main>
    </div>
  )
}

export default Dashboard