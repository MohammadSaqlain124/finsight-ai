const BASE_URL = 'http://localhost:8000'  // dev backend; becomes a Vite env var at deploy time

export async function apiFetch(path, { method = 'GET', body, form } = {}) {
  const options = { method, headers: {} }

  if (form !== undefined) {
    // OAuth2PasswordRequestForm expects x-www-form-urlencoded, not JSON
    options.headers['Content-Type'] = 'application/x-www-form-urlencoded'
    options.body = new URLSearchParams(form).toString()
  } else if (body !== undefined) {
    options.headers['Content-Type'] = 'application/json'
    options.body = JSON.stringify(body)
  }

  const res = await fetch(`${BASE_URL}${path}`, options)
  const data = await res.json().catch(() => null)

  if (!res.ok) {
    const detail = data?.detail
    throw new Error(typeof detail === 'string' ? detail : 'Request failed. Please try again.')
  }
  return data
}