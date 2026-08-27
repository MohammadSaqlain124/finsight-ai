export function formatINR(amount) {
  const n = Number(amount) || 0
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(n)
}

export function formatMonth(ym) {
  const [y, m] = String(ym).split('-').map(Number)
  if (!y || !m) return ym
  return new Date(y, m - 1, 1).toLocaleString('en-IN', { month: 'short', year: 'numeric' })
}