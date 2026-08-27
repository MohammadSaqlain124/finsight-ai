import { getToken } from './auth'

const BASE_URL = 'http://localhost:8000'

export async function apiFetch(path, { method = 'GET', body, form, formData } = {}) {
  const options = { method, headers: {} }

  const token = getToken()
  if (token) {
    options.headers['Authorization'] = `Bearer ${token}`
  }

  if (formData !== undefined) {
    // multipart/form-data — DON'T set Content-Type; the browser must set it
    // itself so it can include the multipart boundary marker.
    options.body = formData
  } else if (form !== undefined) {
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