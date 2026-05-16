import axios from 'axios'

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8080'

const request = axios.create({
  baseURL: API_BASE_URL,
  timeout: 1200000
})

request.interceptors.request.use(
  (config) => {
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

request.interceptors.response.use(
  (response) => {
    return response
  },
  (error) => {
    console.error('API request error:', error)
    return Promise.reject(error)
  }
)

export default request
export { API_BASE_URL }
