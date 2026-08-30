import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { apiFetch } from '../lib/api'
import { formatINR } from '../lib/format'
import Button from '../components/Button'
import TextField from '../components/TextField'
import BackgroundThreads from '../components/BackgroundThreads'
import styles from './Upload.module.css'

function Upload() {
  const [file, setFile] = useState(null)
  const [password, setPassword] = useState('')
  const [preview, setPreview] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [confirming, setConfirming] = useState(false)
  const navigate = useNavigate()

  async function handleUpload(e) {
    e.preventDefault()
    if (!file) return
    setError('')
    setPreview(null)
    setLoading(true)
    try {
      const formData = new FormData()
      formData.append('file', file)
      if (password) formData.append('password', password)
      const statement = await apiFetch('/api/statements/upload', { method: 'POST', formData })
      const previewData = await apiFetch(`/api/statements/${statement.id}/preview`)
      setPreview({ ...previewData, statementId: statement.id })
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  async function handleConfirm() {
    setError('')
    setConfirming(true)
    try {
      await apiFetch(`/api/statements/${preview.statementId}/confirm`, { method: 'POST' })
      navigate('/dashboard')
    } catch (err) {
      setError(err.message)
      setConfirming(false)
    }
  }

  return (
    <div className={styles.page}>
      <BackgroundThreads />

      <header className={styles.header}>
        <svg className={styles.veins} viewBox="0 0 1200 120" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <linearGradient id="uploadGold" x1="0" y1="0" x2="1" y2="0">
              <stop offset="0" stopColor="#E8C989" />
              <stop offset="0.5" stopColor="#C9A15A" />
              <stop offset="1" stopColor="#8C6A2E" />
            </linearGradient>
          </defs>
          <g fill="none" stroke="url(#uploadGold)" strokeLinecap="round">
            <path d="M-20 40 C 260 14, 470 72, 700 44 S 1040 26, 1220 60" strokeWidth="1.2" opacity="0.85" />
            <path d="M-20 84 C 300 66, 560 100, 780 78 S 1080 92, 1220 74" strokeWidth="0.9" opacity="0.6" />
            <path d="M160 -10 C 360 56, 560 30, 860 90 S 1140 62, 1240 34" strokeWidth="0.6" opacity="0.4" />
          </g>
        </svg>
        <span className={styles.wordmark}>FinSight AI</span>
        <Link to="/dashboard" className={styles.back}>← Dashboard</Link>
      </header>

      <main className={styles.main}>
        <h1 className={styles.title}>Upload a statement</h1>
        <p className={styles.lead}>
          Choose a CSV or PDF bank statement. FinSight parses and cleans it, then shows a
          preview. Nothing is saved until you confirm. For a password-protected PDF, enter
          its password below.
        </p>

        <form onSubmit={handleUpload} className={styles.panel}>
          <div className={styles.field}>
            <label htmlFor="statementFile" className={styles.fieldLabel}>Statement file</label>
            <input
              id="statementFile"
              type="file"
              accept=".csv,.pdf"
              onChange={(e) => setFile(e.target.files[0] || null)}
              className={styles.fileInput}
            />
          </div>
          <TextField
            label="PDF password"
            id="pdfPassword"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Only for password-protected PDFs"
          />
          <Button type="submit" variant="primary" disabled={!file || loading}>
            {loading ? 'Uploading…' : 'Upload & preview'}
          </Button>
        </form>

        {error && <p className={styles.error}>{error}</p>}

        {preview && (
          <section>
            <div className={styles.previewHead}>
              <span className={styles.tick} />
              <h2 className={styles.previewTitle}>Preview</h2>
              <span className={styles.rule} />
            </div>
            <p className={styles.meta}>
              Parsed <strong>{preview.transaction_count}</strong> transactions
              from <strong>{preview.raw_row_count}</strong> rows
              {preview.transaction_count > 20 && ', showing the first 20'}.
            </p>

            <div className={styles.tableWrap}>
              <table className={styles.table}>
                <thead>
                  <tr>
                    <th>Date</th>
                    <th>Description</th>
                    <th className={styles.right}>Amount</th>
                  </tr>
                </thead>
                <tbody>
                  {preview.preview.map((t, i) => (
                    <tr key={i}>
                      <td className={styles.mono}>{t.date}</td>
                      <td>{t.description}</td>
                      <td className={`${styles.right} figure ${t.transaction_type === 'expense' ? 'figure--negative' : ''}`}>
                        {t.transaction_type === 'expense' ? formatINR(-t.amount) : formatINR(t.amount)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className={styles.confirmRow}>
              <Button variant="primary" onClick={handleConfirm} disabled={confirming}>
                {confirming ? 'Importing…' : `Confirm & import ${preview.transaction_count} transactions`}
              </Button>
              <span className={styles.hint}>You can review everything on the dashboard after.</span>
            </div>
          </section>
        )}
      </main>
    </div>
  )
}

export default Upload