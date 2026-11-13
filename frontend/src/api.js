import { ref } from 'vue'

const usernameKey = 'petshop.username'
const accessKey = 'petshop.access'
const refreshKey = 'petshop.refresh'
export const username = ref(sessionStorage.getItem(usernameKey) || '')
export const notice = ref('')

export function signedIn() {
  return Boolean(sessionStorage.getItem(refreshKey))
}

export function signOut() {
  for (const key of [usernameKey, accessKey, refreshKey]) sessionStorage.removeItem(key)
  username.value = ''
  notice.value = ''
}

async function send(path, method, data, access) {
  const headers = { Accept: 'application/json' }
  if (data !== undefined) headers['Content-Type'] = 'application/json'
  if (access) headers.Authorization = 'Bearer ' + access
  try {
    return await fetch(path, { method, headers, body: JSON.stringify(data) })
  } catch {
    throw new Error('Не удалось связаться с сервером.')
  }
}

async function read(response) {
  if (response.status === 204) return null
  const data = await response.json().catch(() => null)
  if (response.ok && data !== null) return data
  const labels = {
    name: 'Название', species: 'Вид', breed: 'Порода',
    age_months: 'Возраст', price: 'Цена', description: 'Описание',
  }
  const errors = data && Object.entries(data)
    .map(([field, value]) => {
      const message = Array.isArray(value) ? value.join(' ') : value
      return labels[field] ? labels[field] + ': ' + message : message
    })
    .join(' ')
  throw new Error(errors || 'Сервер вернул ошибку (' + response.status + ').')
}

export async function signIn(login, password) {
  const tokens = await read(await send('/api/token/', 'POST', { username: login, password }))
  sessionStorage.setItem(accessKey, tokens.access)
  sessionStorage.setItem(refreshKey, tokens.refresh)
  sessionStorage.setItem(usernameKey, login)
  username.value = login
}

export async function api(path, method = 'GET', data) {
  let response = await send(path, method, data, sessionStorage.getItem(accessKey))
  if (response.status === 401 && signedIn()) {
    const refresh = sessionStorage.getItem(refreshKey)
    const refreshed = await send('/api/token/refresh/', 'POST', { refresh })
    if (refreshed.status === 401) {
      signOut()
      throw new Error('Время входа истекло. Войдите ещё раз.')
    }
    const tokens = await read(refreshed)
    if (sessionStorage.getItem(refreshKey) !== refresh) {
      throw new Error('Войдите ещё раз.')
    }
    sessionStorage.setItem(accessKey, tokens.access)
    response = await send(path, method, data, tokens.access)
  }
  return read(response)
}
