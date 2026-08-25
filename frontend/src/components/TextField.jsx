import styles from './TextField.module.css'

function TextField({ label, id, type = 'text', value, onChange, error, ...props }) {
  return (
    <div className={styles.field}>
      <label htmlFor={id} className={styles.label}>{label}</label>
      <input
        id={id}
        type={type}
        value={value}
        onChange={onChange}
        className={`${styles.input} ${error ? styles.inputError : ''}`}
        aria-invalid={error ? 'true' : undefined}
        {...props}
      />
      {error && <p className={styles.error}>{error}</p>}
    </div>
  )
}

export default TextField