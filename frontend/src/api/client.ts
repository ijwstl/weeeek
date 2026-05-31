const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '/api/v1'

export interface ApiResponse<T> {
  data: T
  request_id?: string | null
}

export async function apiGet<T>(path: string): Promise<T> {
  return apiRequest<T>(path, { method: 'GET' })
}

export async function apiPut<T, TPayload = unknown>(path: string, payload: TPayload): Promise<T> {
  return apiRequest<T>(path, {
    method: 'PUT',
    body: JSON.stringify(payload)
  })
}

export async function apiPost<T, TPayload = unknown>(path: string, payload: TPayload): Promise<T> {
  return apiRequest<T>(path, {
    method: 'POST',
    body: JSON.stringify(payload)
  })
}

export async function apiPatch<T, TPayload = unknown>(path: string, payload: TPayload): Promise<T> {
  return apiRequest<T>(path, {
    method: 'PATCH',
    body: JSON.stringify(payload)
  })
}

export async function apiDelete<T>(path: string): Promise<T> {
  return apiRequest<T>(path, { method: 'DELETE' })
}

async function apiRequest<T>(path: string, init: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      Accept: 'application/json',
      'Content-Type': 'application/json',
      ...init.headers
    }
  })

  if (!response.ok) {
    throw new Error(`API request failed: ${response.status}`)
  }

  const body = (await response.json()) as ApiResponse<T>
  return body.data
}
