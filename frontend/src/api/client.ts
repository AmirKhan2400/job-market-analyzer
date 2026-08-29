import { ApiError } from '../types/api'

const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? ''

type JsonBody = Record<string, unknown> | unknown[] | string | null

function messageFromFastApi(body: JsonBody): string | null {
  if (body === null || typeof body !== 'object' || Array.isArray(body)) {
    return typeof body === 'string' ? body : null
  }

  const detail = 'detail' in body ? body.detail : undefined

  if (typeof detail === 'string') {
    return detail
  }

  if (Array.isArray(detail) && detail.length > 0) {
    const first = detail[0]
    if (typeof first === 'object' && first !== null && 'msg' in first) {
      return String(first.msg)
    }
  }

  return null
}

async function parseJsonSafe(response: Response): Promise<JsonBody> {
  try {
    return (await response.json()) as JsonBody
  } catch {
    return null
  }
}

export async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const url = `${BASE_URL}${path}`

  let response: Response
  try {
    response = await fetch(url, {
      ...options,
      credentials: 'include',
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    })
  } catch {
    throw new ApiError(
      'Unable to reach the server. Is the backend running?',
      0,
    )
  }

  if (!response.ok) {
    const body = await parseJsonSafe(response)
    throw new ApiError(
      messageFromFastApi(body) ?? `Request failed (${response.status})`,
      response.status,
      body,
    )
  }

  return (await response.json()) as T
}
