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
  const [subs, setSubs] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    apiFetch('/api/analytics/summary')
      .then(setSummary)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))

    // Best-effort: if subscriptions fails, we simply don't show that section.
    apiFetch('/api/analytics/subscriptions')
      .then(setSubs)
      .catch(() => {})
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
        <div className={styles.actions}>
          <Button variant="secondary" onClick={() => navigate('/upload')}>Upload</Button>
          <Button variant="secondary" onClick={handleLogout}>Sign out</Button>
        </div>
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

            {summary.spending_by_category.length > 0 && (
              <section className={styles.section}>
                <h2 className={styles.sectionTitle}>Where your money went</h2>
                <div className={styles.breakdown}>
                  {summary.spending_by_category.map((c) => {
                    const pct = summary.total_expenses > 0
                      ? (c.total / summary.total_expenses) * 100
                      : 0
                    return (
                      <div key={c.category} className={styles.breakdownRow}>
                        <div className={styles.breakdownHead}>
                          <span className={styles.breakdownCat}>{c.category}</span>
                          <span className={`figure figure--negative ${styles.breakdownAmt}`}>
                            {formatINR(-c.total)}
                          </span>
                        </div>
                        <div className={styles.bar}>
                          <div className={styles.barFill} style={{ width: `${pct}%` }} />
                        </div>
                        <span className={styles.breakdownPct}>{pct.toFixed(0)}% of spending</span>
                      </div>
                    )
                  })}
                </div>

                {summary.biggest_expense && (
                  <p className={styles.biggest}>
                    Biggest single expense: <strong>{summary.biggest_expense.description}</strong>
                    {' — '}
                    <span className="figure figure--negative">
                      {formatINR(-summary.biggest_expense.amount)}
                    </span>
                    {summary.biggest_expense.date ? ` on ${summary.biggest_expense.date}` : ''}.
                  </p>
                )}
              </section>
            )}

            {subs && subs.count > 0 && (
              <section className={styles.section}>
                <h2 className={styles.sectionTitle}>Recurring payments</h2>
                <p className={styles.muted}>
                  {subs.count} detected · about{' '}
                  <span className="figure">{formatINR(subs.estimated_monthly_total)}</span> per month
                </p>
                <div className={styles.subsList}>
                  {subs.subscriptions.map((s, i) => (
                    <div key={i} className={styles.subRow}>
                      <div className={styles.subInfo}>
                        <span className={styles.subMerchant}>{s.sample_description}</span>
                        <span className={styles.subMeta}>
                          {s.frequency} · {s.occurrences} payments · {Math.round(s.confidence * 100)}% confidence
                        </span>
                      </div>
                      <div className={styles.subAmounts}>
                        <span className={`figure figure--negative ${styles.subAmt}`}>
                          {formatINR(-s.average_amount)}
                        </span>
                        <span className={styles.subAnnual}>
                          ≈ {formatINR(s.estimated_annual_cost)}/yr
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              </section>
            )}
          </>
        )}
      </main>
    </div>
  )
}

export default Dashboard