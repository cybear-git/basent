import { useState, useEffect } from 'react'
import api from '../../services/api'
import { Search, Filter, ChevronLeft, ChevronRight } from 'lucide-react'
import './PublicWorks.css'

interface Department {
  id: number
  code: string
  full_name: string
  short_name: string
}

interface ResultType {
  id: number
  code: string
  display_name: string
}

interface Publication {
  id: number
  title: string
  author: string
  year: number
  department: {
    id: number
    code: string
    short_name: string
    full_name: string
  } | null
  result: {
    id: number
    code: string
    display_name: string
  } | null
  status: string
  owner_username: string
  created_at: string
}

const PublicWorks: React.FC = () => {
  const [publications, setPublications] = useState<Publication[]>([])
  const [departments, setDepartments] = useState<Department[]>([])
  const [resultTypes, setResultTypes] = useState<ResultType[]>([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [department, setDepartment] = useState('')
  const [year, setYear] = useState('')
  const [result, setResult] = useState('')
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)

  const YEARS = [
    { value: '', label: 'Все годы' },
    { value: '2026', label: '2026' },
    { value: '2025', label: '2025' },
    { value: '2024', label: '2024' },
    { value: '2023', label: '2023' },
    { value: '2022', label: '2022' },
    { value: '2021', label: '2021' },
    { value: '2020', label: '2020' },
  ]

  useEffect(() => {
    loadDictionaries()
  }, [])

  useEffect(() => {
    loadPublications()
  }, [search, department, year, result, page])

  const loadDictionaries = async () => {
    try {
      const [deptRes, resultRes] = await Promise.all([
        api.get('/departments/'),
        api.get('/result-types/')
      ])
      setDepartments(deptRes.data.results || deptRes.data)
      setResultTypes(resultRes.data.results || resultRes.data)
    } catch (error) {
      console.error('Error loading dictionaries:', error)
    }
  }

  const loadPublications = async () => {
    try {
      const params = new URLSearchParams()
      params.append('page', page.toString())
      if (search) params.append('search', search)
      if (department) params.append('department', department)
      if (year) params.append('year', year)
      if (result) params.append('result', result)
      
      const response = await api.get(`/publications/?${params}`)
      const data = response.data
      setPublications(data.results || data)
      setTotalPages(Math.ceil((data.count || 0) / 20))
    } catch (error) {
      console.error('Error loading publications:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="public-works">
      <div className="page-header">
        <h1>Публикации и мероприятия</h1>
        <p className="subtitle">База научных трудов и достижений</p>
      </div>

      <div className="filters">
        <div className="search-box">
          <Search size={20} />
          <input
            type="text"
            placeholder="Поиск по названию, автору..."
            value={search}
            onChange={(e) => { setSearch(e.target.value); setPage(1); }}
          />
        </div>

        <div className="filter-group">
          <Filter size={20} />
          <select value={department} onChange={(e) => { setDepartment(e.target.value); setPage(1); }}>
            <option value="">Все кафедры</option>
            {departments.map(d => (
              <option key={d.id} value={d.code}>{d.short_name || d.full_name}</option>
            ))}
          </select>

          <select value={year} onChange={(e) => { setYear(e.target.value); setPage(1); }}>
            {YEARS.map(y => <option key={y.value} value={y.value}>{y.label}</option>)}
          </select>

          <select value={result} onChange={(e) => { setResult(e.target.value); setPage(1); }}>
            <option value="">Все результаты</option>
            {resultTypes.map(r => (
              <option key={r.id} value={r.code}>{r.display_name}</option>
            ))}
          </select>
        </div>
      </div>

      {loading ? (
        <div className="loading">Загрузка...</div>
      ) : (
        <>
          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Название</th>
                  <th>Автор</th>
                  <th>Год</th>
                  <th>Кафедра</th>
                  <th>Результат</th>
                </tr>
              </thead>
              <tbody>
                {publications.map(pub => (
                  <tr key={pub.id}>
                    <td className="title-cell">{pub.title}</td>
                    <td>{pub.author}</td>
                    <td>{pub.year}</td>
                    <td>{pub.department?.short_name || pub.department?.full_name || '-'}</td>
                    <td>
                      <span className={`result-badge ${pub.result?.code || ''}`}>
                        {pub.result?.code === 'winner' ? '🏆' : pub.result?.code === 'prize_winner' ? '🥈' : ''} {pub.result?.display_name || '-'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {totalPages > 1 && (
            <div className="pagination">
              <button onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1}>
                <ChevronLeft size={20} />
              </button>
              <span>Страница {page} из {totalPages}</span>
              <button onClick={() => setPage(p => Math.min(totalPages, p + 1))} disabled={page === totalPages}>
                <ChevronRight size={20} />
              </button>
            </div>
          )}
        </>
      )}
    </div>
  )
}

export default PublicWorks