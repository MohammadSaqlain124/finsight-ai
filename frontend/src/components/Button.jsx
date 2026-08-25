import styles from './Button.module.css'

function Button({ children, variant = 'primary', type = 'button', disabled = false, ...props }) {
  return (
    <button
      type={type}
      disabled={disabled}
      className={`${styles.button} ${styles[variant]}`}
      {...props}
    >
      {children}
    </button>
  )
}

export default Button