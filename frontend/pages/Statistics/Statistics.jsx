import { useState, useEffect } from 'react'
import api from '../../services/api'
import { useReferenceData } from '../../services/reference'
import * as XLSX from 'xlsx'
import { Download, BarChart3, PieChart, TrendingUp } from 'lucide-react'
import './Statistics.css'

const Statistics = () => {
  const { reference } = useReferenceData()
  const [yearFrom, setYearFrom] = useState('')
  const [yearTo, setYearTo] = useState('')
  const [department, setDepartment] = useState('')
  const [stats, setStats] = useState(null)
  const [publications, setPublications] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadData()
  }, [yearFrom, yearTo, department])

  const loadData = async () => {
    setLoading(true)
    try {
      const params = new URLSearchParams()
      if (yearFrom) params.append('year_from', yearFrom)
      if (yearTo) params.append('year_to', yearTo)
      if (department) params.append('department', department)

      const [statsRes, pubsRes] = await Promise.all([
        api.get(`/publications/statistics/?${params}`),
        api.get(`/publications/?${params}&page_size=1000`)
      ])

      setStats(statsRes.data)
      setPublications(pubsRes.data.results || pubsRes.data)
    } catch (error) {
      console.error('Error loading statistics:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleExport = () => {
    if (!publications || publications.length === 0) return

    const data = publications.map((pub) => ({
      'Название': pub.title,
      'Автор': pub.author,
      'Год': pub.year,
      'Кафедра': pub.department_display || pub.department,
      'Результат': pub.result_display || '-',
      'Статус': pub.status_display || pub.status,
      'Дата создания': new Date(pub.created_at).toLocaleDateString('ru-RU'),
    }))

    const ws = XLSX.utils.json_to_sheet(data)
    const wb = XLSX.utils.book_new()
    XLSX.utils.book_append_sheet(wb, ws, 'Публикации')

    const fileName = `публикации_${new Date().toISOString().split('T')[0]}.xlsx`
    XLSX.writeFile(wb, fileName)
  }

  const departments = reference?.departments || []
  const maxYearCount = stats?.by_year?.reduce((max, item) =>
    item.count > max ? item.count : max, 0) || 0

  return (
    <div className="statistics">
      <div className="stats-header">
        <h1>Статистика</h1>
        <button className="btn-export" onClick={handleExport} disabled={!publications?.length}>
          <Download size={18} />
          Выгрузить в XLSX
        </button>
      </div>

      <div className="filters-bar">
        <div className="filter-item">
          <label>Год от</label>
          <input
            type="number"
            value={yearFrom}
            onChange={(e) => setYearFrom(e.target.value)}
            placeholder="2020"
            min="2000"
            max="2030"
          />
        </div>
        <div className="filter-item">
          <label>Год до</label>
          <input
            type="number"
            value={yearTo}
            onChange={(e) => setYearTo(e.target.value)}
            placeholder="2025"
            min="2000"
            max="2030"
          />
        </div>
        <div className="filter-item">
          <label>Кафедра</label>
          <select value={department} onChange={(e) => setDepartment(e.target.value)}>
            <option value="">Все кафедры</option>
            {departments.map(d => (
              <option key={d.code} value={d.code}>{d.label}</option>
            ))}
          </select>
        </div>
      </div>

      {loading ? (
        <div className="loading">Загрузка статистики...</div>
      ) : (
        <>
          <div className="stats-cards">
            <div className="stat-card total">
              <div className="stat-icon"><BarChart3 size={24} /></div>
              <div className="stat-info">
                <span className="stat-value">{stats?.total || 0}</span>
                <span className="stat-label">Всего публикаций</span>
              </div>
            </div>
          </div>

          <div className="charts-grid">
            <div className="chart-card">
              <h3><TrendingUp size={18} /> По годам</h3>
              <div className="bar-chart">
                {stats?.by_year?.map((item) => (
                  <div key={item.year} className="bar-item">
                    <span className="bar-label">{item.year}</span>
                    <div className="bar-track">
                      <div
                        className="bar-fill"
                        style={{ width: `${maxYearCount ? (item.count / maxYearCount) * 100 : 0}%` }}
                      />
                    </div>
                    <span className="bar-value">{item.count}</span>
                  </div>
                ))}
                {(!stats?.by_year || stats.by_year.length === 0) && (
                  <p className="no-data">Нет данных</p>
                )}
              </div>
            </div>

            <div className="chart-card">
              <h3><PieChart size={18} /> По кафедрам</h3>
              <div className="pie-chart">
                {stats?.by_department?.map((item, idx) => {
                  const percentage = stats.total > 0 ? Math.round((item.count / stats.total) * 100) : 0
                  const colors = ['#4361ee', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#14b8a6', '#f97316', '#06b6d4', '#84cc16', '#6366f1']
                  return (
                    <div key={item.department} className="pie-item">
                      <div
                        className="pie-color"
                        style={{ backgroundColor: colors[idx % colors.length] }}
                      />
                      <span className="pie-label">
                        {item.department_display || item.department}
                      </span>
                      <span className="pie-value">{item.count} ({percentage}%)</span>
                    </div>
                  )
                })}
                {(!stats?.by_department || stats.by_department.length === 0) && (
                  <p className="no-data">Нет данных</p>
                )}
              </div>
            </div>

            <div className="chart-card">
              <h3><BarChart3 size={18} /> По результатам</h3>
              <div className="result-chart">
                {stats?.by_result?.map((item) => {
                  const color = item.result === 'winner' ? '#10b981' :
                               item.result === 'prize_winner' ? '#f59e0b' : '#6b7280'
                  return (
                    <div key={item.result} className="result-item">
                      <span className="result-label" style={{ color }}>{item.result_display || '-'}</span>
                      <span className="result-value">{item.count}</span>
                    </div>
                  )
                })}
                {(!stats?.by_result || stats.by_result.length === 0) && (
                  <p className="no-data">Нет данных</p>
                )}
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  )
}

export default Statistics