import axios from 'axios'

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
})

export const createScan = (target) =>
  api.post('/scans', { target }).then(r => r.data)

export const listScans = () =>
  api.get('/scans').then(r => r.data)

export const getScan = (id) =>
  api.get(`/scans/${id}`).then(r => r.data)

export const deleteScan = (id) =>
  api.delete(`/scans/${id}`).then(r => r.data)

export const getStats = () =>
  api.get('/stats').then(r => r.data)

export default api
