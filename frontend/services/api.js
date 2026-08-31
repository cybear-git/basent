import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  config.headers['Content-Type'] = 'application/json'
  return config
})

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config

    if (error.response?.status === 401 && !originalRequest?._retry) {
      originalRequest._retry = true

      try {
        const refresh = localStorage.getItem('refresh_token')
        if (!refresh) {
          throw new Error('No refresh token')
        }
        const res = await axios.post(`${api.defaults.baseURL}/users/auth/refresh/`, { refresh })
        const { access } = res.data

        localStorage.setItem('access_token', access)
        originalRequest.headers.Authorization = `Bearer ${access}`

        return api(originalRequest)
      } catch (e) {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        window.location.href = '/'
      }
    }

    return Promise.reject(error)
  }
)

export const parseValidationErrors = (error) => {
  const errors = {}
  const data = error.response?.data

  if (!data) {
    return { general: 'Неизвестная ошибка сервера' }
  }

  if (Array.isArray(data.non_field_errors)) {
    errors.general = data.non_field_errors.join('. ')
  }

  Object.keys(data).forEach(key => {
    if (key !== 'non_field_errors' && key !== 'detail') {
      const value = data[key]
      if (Array.isArray(value)) {
        errors[key] = value.join('. ')
      } else if (typeof value === 'string') {
        errors[key] = value
      }
    }
  })

  if (Object.keys(errors).length === 0 && data.detail) {
    errors.general = data.detail
  }

  return errors
}

export default api