import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { apiFetch } from '../lib/api'
import { formatINR, formatMonth } from '../lib/format'
import Button from '../components/Button'
import styles from './Dashboard.module.css'

// Financial good/bad tone for a month-over-month change.
// For expenses, going up is bad; for income and net, up is good.
function changeTone(metric, entry) {
  if (!entry || entry.difference === 0) return 'flat'
  const upIsGood = metric !== 'expenses'
  const wentUp = entry.difference > 0
  return wentUp === upIsGood ? 'good' : 'bad'
}

// Editorial section header: serif title + trailing hairline rule.
function SectionHead({ title }) {
  return (
    <div className={styles.sectionHead}>
      <h2 className={styles.sectionTitle}>{title}</h2>
      <span className={styles.sectionRule} />
    </div>
  )
}

function Dashboard() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [summary, setSummary] = useState(null)
  const [subs, setSubs] = useState(null)
  const [monthly, setMonthly] = useState(null)
  const [comparison, setComparison] = useState(null)
  const [anomalies, setAnomalies] = useState(null)
  const [anomalyMethod, setAnomalyMethod] = useState('zscore')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    apiFetch('/api/analytics/summary')
      .then(setSummary)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
    apiFetch('/api/analytics/subscriptions').then(setSubs).catch(() => {})
    apiFetch('/api/analytics/monthly').then(setMonthly).catch(() => {})
    apiFetch('/api/analytics/comparison').then(setComparison).catch(() => {})
  }, [])

  useEffect(() => {
    apiFetch(`/api/analytics/anomalies?method=${anomalyMethod}`)
      .then(setAnomalies)
      .catch(() => {})
  }, [anomalyMethod])

  function handleLogout() {
    logout()
    navigate('/login')
  }

  const hasData = summary && summary.transaction_count > 0
  const maxMonthExpense =
    monthly && monthly.months.length > 0
      ? Math.max(...monthly.months.map((m) => m.expenses), 1)
      : 1

  return (
    <div className={styles.page}>
      <header className={styles.header}>
        <div className={styles.brandwrap}>
          <span className={styles.wordmark}>FinSight AI</span>
          <span className={styles.brandsub}>
            {user ? `Welcome back, ${user.full_name}` : 'Personal finance'}
          </span>
        </div>
        <div className={styles.actions}>
          <button className={styles.hbtn} onClick={() => navigate('/upload')}>Upload</button>
          <button className={styles.hbtn} onClick={handleLogout}>Sign out</button>
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
              <p className={styles.heroEyebrow}>Net savings</p>
              <p className={`figure ${styles.heroFigure} ${summary.net_savings < 0 ? 'figure--negative' : ''}`}>
                {summary.net_savings >= 0 ? '+' : ''}{formatINR(summary.net_savings)}
              </p>
              <p className={styles.heroSub}>
                You kept {summary.savings_rate}% of your income across {summary.transaction_count} transactions.
              </p>
              <span className={styles.privacy}>
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor"
                     strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                  <rect x="3" y="11" width="18" height="11" rx="2" />
                  <path d="M7 11V7a5 5 0 0 1 10 0v4" />
                </svg>
                Account numbers and identifiers are removed before your statement is stored.
              </span>
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
              <section className={styles.block}>
                <SectionHead title="Where your money went" />
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

            {monthly && monthly.months.length > 0 && (
              <section className={styles.block}>
                <SectionHead title="Monthly trend" />
                <div className={styles.monthList}>
                  {monthly.months.map((m) => (
                    <div key={m.month} className={styles.monthRow}>
                      <div className={styles.monthHead}>
                        <span className={styles.monthLabel}>{formatMonth(m.month)}</span>
                        <span className={`figure figure--negative ${styles.monthAmt}`}>
                          {formatINR(-m.expenses)}
                        </span>
                      </div>
                      <div className={styles.bar}>
                        <div className={styles.barFill} style={{ width: `${(m.expenses / maxMonthExpense) * 100}%` }} />
                      </div>
                      <span className={styles.monthMeta}>
                        income <span className="figure">{formatINR(m.income)}</span>
                        {'  ·  net '}
                        <span className={`figure ${m.net_savings < 0 ? 'figure--negative' : ''}`}>
                          {m.net_savings >= 0 ? '+' : ''}{formatINR(m.net_savings)}
                        </span>
                      </span>
                    </div>
                  ))}
                </div>
              </section>
            )}

            {comparison && comparison.comparable && (
              <section className={styles.block}>
                <SectionHead title="What changed" />
                <p className={styles.muted}>
                  {formatMonth(comparison.current_month)} vs {formatMonth(comparison.previous_month)}
                </p>

                {comparison.what_changed.length > 0 ? (
                  <ul className={styles.insights} style={{ marginTop: '1rem' }}>
                    {comparison.what_changed.map((line, i) => (
                      <li key={i} className={styles.insight}>{line}</li>
                    ))}
                  </ul>
                ) : (
                  <p className={styles.muted} style={{ marginTop: '0.75rem' }}>
                    Spending held steady between these two months.
                  </p>
                )}

                <div className={styles.compareGrid}>
                  {[
                    { label: 'Income', entry: comparison.income, metric: 'income', showPct: true },
                    { label: 'Expenses', entry: comparison.expenses, metric: 'expenses', showPct: true },
                    { label: 'Net', entry: comparison.net_savings, metric: 'net', showPct: false },
                  ].map(({ label, entry, metric, showPct }) => {
                    const tone = changeTone(metric, entry)
                    return (
                      <div key={label} className={styles.compareCard}>
                        <p className={styles.cardLabel}>{label}</p>
                        <p className={`figure ${styles.compareCur} ${entry.current < 0 ? 'figure--negative' : ''}`}>
                          {formatINR(entry.current)}
                        </p>
                        <p className={`${styles.compareDelta} ${styles['tone_' + tone]}`}>
                          {entry.difference >= 0 ? '+' : ''}{formatINR(entry.difference)}
                          {showPct && entry.percent_change !== null
                            ? ` (${entry.percent_change > 0 ? '+' : ''}${entry.percent_change}%)`
                            : ''}
                          {' '}vs {formatMonth(comparison.previous_month)}
                        </p>
                      </div>
                    )
                  })}
                </div>
              </section>
            )}

            {subs && subs.count > 0 && (
              <section className={styles.block}>
                <SectionHead title="Recurring payments" />
                <p className={styles.muted}>
                  {subs.count} detected · about{' '}
                  <span className="figure">{formatINR(subs.estimated_monthly_total)}</span> per month
                </p>
                <div className={styles.subsList} style={{ marginTop: '1rem' }}>
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

            <section className={styles.block}>
              <SectionHead title="Unusual transactions" />
              <div className={styles.toggle}>
                <button
                  className={`${styles.toggleBtn} ${anomalyMethod === 'zscore' ? styles.toggleBtnActive : ''}`}
                  onClick={() => setAnomalyMethod('zscore')}
                >
                  Z-score
                </button>
                <button
                  className={`${styles.toggleBtn} ${anomalyMethod === 'iqr' ? styles.toggleBtnActive : ''}`}
                  onClick={() => setAnomalyMethod('iqr')}
                >
                  IQR
                </button>
              </div>

              {anomalies && !anomalies.enough_data && (
                <p className={styles.muted}>{anomalies.reason}</p>
              )}

              {anomalies && anomalies.enough_data && anomalies.anomaly_count === 0 && (
                <p className={styles.muted}>No unusual transactions flagged with this method.</p>
              )}

              {anomalies && anomalies.enough_data && anomalies.anomaly_count > 0 && (
                <>
                  <p className={styles.muted}>
                    {anomalies.anomaly_count} flagged — anything above{' '}
                    <span className="figure">{formatINR(anomalies.upper_threshold)}</span>, versus an average
                    expense of <span className="figure">{formatINR(anomalies.average_expense)}</span>.
                  </p>
                  <div className={styles.anomList} style={{ marginTop: '1rem' }}>
                    {anomalies.anomalies.map((a) => (
                      <div key={a.id} className={styles.anomRow}>
                        <div className={styles.anomHead}>
                          <span className={styles.anomDesc}>{a.description}</span>
                          <span className="figure figure--negative">{formatINR(-a.amount)}</span>
                        </div>
                        <p className={styles.anomReason}>{a.reason}</p>
                        <span className={styles.anomMeta}>{a.category} · {a.date}</span>
                      </div>
                    ))}
                  </div>
                </>
              )}
            </section>
          </>
        )}
      </main>
    </div>
  )
}

export default Dashboard