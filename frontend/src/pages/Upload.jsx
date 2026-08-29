import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { apiFetch } from '../lib/api'
import { formatINR } from '../lib/format'
import Button from '../components/Button'
import TextField from '../components/TextField'
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
      if (password) formData.append('password', password)   // only sent when provided
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
      <header className={styles.topbar}>
        <p className={styles.wordmark}>FinSight AI</p>
        <Link to="/dashboard" className={styles.back}>← Dashboard</Link>
      </header>

      <main className={styles.main}>
        <h1 className={styles.title}>Upload a statement</h1>
        <p className={styles.muted}>
          Choose a CSV or PDF bank statement. FinSight parses and cleans it, then shows a
          preview — nothing is saved until you confirm. For a password-protected PDF, enter
          its password below.
        </p>

        <form onSubmit={handleUpload} className={styles.uploader}>
          <input
            type="file"
            accept=".csv,.pdf"
            onChange={(e) => setFile(e.target.files[0] || null)}
            className={styles.fileInput}
          />
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
          <section className={styles.previewBlock}>
            <p className={styles.previewMeta}>
              Parsed <strong>{preview.transaction_count}</strong> transactions
              from <strong>{preview.raw_row_count}</strong> rows
              {preview.transaction_count > 20 && ' — showing the first 20'}.
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
              <span className={styles.muted}>You can review everything on the dashboard after.</span>
            </div>
          </section>
        )}
      </main>
    </div>
  )
}

export default Upload