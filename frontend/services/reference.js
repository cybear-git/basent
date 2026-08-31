import { useEffect, useState } from 'react'
import api from './api'

let cache = null

export async function getReferenceData(force = false) {
  if (cache && !force) return cache
  const res = await api.get('/reference/')
  cache = res.data
  return cache
}

export function useReferenceData() {
  const [reference, setReference] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    getReferenceData()
      .then(setReference)
      .catch(() => setReference(null))
      .finally(() => setLoading(false))
  }, [])

  return { reference, loading }
}

export function labelFor(list, code) {
  if (!list || !Array.isArray(list)) return ''
  const item = list.find(i => String(i.code) === String(code))
  return item ? item.label : ''
}