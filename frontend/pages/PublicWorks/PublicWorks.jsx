import { useState, useEffect, useCallback } from 'react'
import api from '../../services/api'
import { useAuth } from '../../context/AuthContext'
import { useToast } from '../../components/Toast'
import { useReferenceData } from '../../services/reference'
import { Search, Filter, ChevronLeft, ChevronRight, X, FileText, Trash2, Download } from 'lucide-react'
import './PublicWorks.css'

const currentYear = new Date().getFullYear()
const YEARS = [
  { value: '', label: 'Все годы' },
  ...Array.from({ length: currentYear - 2015 }, (_, i) => ({
    value: String(currentYear - i),
    label: String(currentYear - i),
  })),
]

const formatDate = (value) => {
  if (!value) return ''
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return String(value)
  const datePart = date.toLocaleDateString('ru-RU')
  const hasTime = typeof value === 'string' && value.includes('T')
  return hasTime
    ? `${datePart} ${date.toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })}`
    : datePart
}

const valueOrDash = (value) => (value === null || value === undefined || value === '' ? '—' : value)

const Field = ({ label, value, full }) => (
  <div className={`detail-field${full ? ' detail-field-full' : ''}`}>
    <span className="detail-field-label">{label}</span>
    <span className="detail-field-value">{valueOrDash(value)}</span>
  </div>
)

const DetailSection = ({ title, children }) => (
  <div className="detail-section">
    <h4 className="detail-section-title">{title}</h4>
    <div className="detail-fields">{children}</div>
  </div>
)

const detectModerationBadge = (status) => {
  if (status === 'approved') return 'badge-success'
  if (status === 'rejected') return 'badge-danger'
  if (status === 'pending') return 'badge-warning'
  return 'badge-neutral'
}

const detectStatusBadge = (pub) => {
  if (pub.status === 'archived') return 'badge-neutral'
  if (pub.status === 'marked_for_deletion') return 'badge-warning'
  return 'badge-success'
}

const PublicWorks = () => {
  const { reference } = useReferenceData()
  const { user } = useAuth()
  const toast = useToast()
  const canDelete = user && (user.role === 'ADMIN' || user.role === 'NIO_STAFF')
  const [publications, setPublications] = useState([])
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [department, setDepartment] = useState('')
  const [year, setYear] = useState('')
  const [result, setResult] = useState('')
  const [page, setPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)

  const [selectedId, setSelectedId] = useState(null)
  const [detail, setDetail] = useState(null)
  const [detailLoading, setDetailLoading] = useState(false)

  useEffect(() => {
    loadPublications()
  }, [search, department, year, result, page])

  const loadPublications = async () => {
    setLoading(true)
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
      setTotalPages(Math.max(1, Math.ceil((data.count || 0) / 20)))
    } catch (error) {
      console.error('Error loading publications:', error)
    } finally {
      setLoading(false)
    }
  }

  const openDetail = async (pub) => {
    setSelectedId(pub.id)
    setDetail(null)
    setDetailLoading(true)
    try {
      const response = await api.get(`/publications/${pub.id}/`)
      setDetail(response.data)
    } catch (error) {
      console.error('Error loading publication detail:', error)
      setDetail(null)
    } finally {
      setDetailLoading(false)
    }
  }

  const closeDetail = useCallback(() => {
    setSelectedId(null)
    setDetail(null)
  }, [])

  const handleSoftDelete = async (e, pub) => {
    e.stopPropagation()
    if (!window.confirm(`Переместить публикацию «${pub.title}» в архив?`)) return
    try {
      await api.delete(`/publications/${pub.id}/`)
      toast.addToast({ type: 'success', title: 'Удалено', message: 'Публикация перемещена в архив.' })
      loadPublications()
    } catch (err) {
      toast.addToast({ type: 'error', title: 'Ошибка', message: 'Не удалось удалить публикацию' })
    }
  }

  const handleExportXLSX = async () => {
    try {
      const response = await api.get('/publications/export/?export_format=xlsx', { responseType: 'blob' })
      const blob = new Blob([response.data], {
        type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      })
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      const date = new Date().toISOString().split('T')[0]
      link.href = url
      link.download = `публикации_все_поля_${date}.xlsx`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
      toast.addToast({ type: 'success', title: 'Готово', message: 'Выгрузка XLSX (все поля) запущена.' })
    } catch (err) {
      console.error('Export error:', err)
      toast.addToast({ type: 'error', title: 'Ошибка', message: 'Не удалось выгрузить XLSX' })
    }
  }

  useEffect(() => {
    if (!selectedId) return
    const onKeyDown = (event) => {
      if (event.key === 'Escape') closeDetail()
    }
    document.addEventListener('keydown', onKeyDown)
    const originalOverflow = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    return () => {
      document.removeEventListener('keydown', onKeyDown)
      document.body.style.overflow = originalOverflow
    }
  }, [selectedId, closeDetail])

  const departments = reference?.departments || []
  const results = reference?.results || []
  const months = reference?.months || []

  const monthLabel = (code) => {
    const found = months.find((m) => m.code === code)
    return found ? found.label : ''
  }

  const ownerName = detail?.owner
    ? `${detail.owner.first_name || ''} ${detail.owner.last_name || ''}`.trim() || detail.owner.username
    : ''
  const moderatorName = detail?.moderated_by
    ? `${detail.moderated_by.first_name || ''} ${detail.moderated_by.last_name || ''}`.trim() || detail.moderated_by.username
    : ''

  return (
    <div className="public-works">
      <div className="page-header">
        <h1>Публикации и мероприятия</h1>
        <p className="subtitle">База научных трудов и достижений</p>
      </div>

      <div className="public-toolbar">
        <button className="md-btn md-btn-filled" onClick={handleExportXLSX}>
          <Download size={18} />
          Выгрузить XLSX (все поля)
        </button>
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
            {departments.map(d => <option key={d.code} value={d.code}>{d.label}</option>)}
          </select>

          <select value={year} onChange={(e) => { setYear(e.target.value); setPage(1); }}>
            {YEARS.map(y => <option key={y.value} value={y.value}>{y.label}</option>)}
          </select>

          <select value={result} onChange={(e) => { setResult(e.target.value); setPage(1); }}>
            <option value="">Все результаты</option>
            {results.map(r => <option key={r.code} value={r.code}>{r.label}</option>)}
          </select>
        </div>
      </div>

      {loading ? (
        <div className="loading">
          <div className="spinner" />
          <span>Загрузка публикаций...</span>
        </div>
      ) : publications.length === 0 ? (
        <div className="empty-state">
          <FileText size={40} />
          <div>Ничего не найдено. Попробуйте изменить параметры поиска.</div>
        </div>
      ) : (
        <>
          <div className="table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Название</th>
                  <th>Автор(ы)</th>
                  <th>Год</th>
                  <th>Кафедра</th>
                  <th>Тип публикации</th>
                  <th>База цитирования</th>
                  <th>Статус автора</th>
                  {canDelete && <th>Действия</th>}
                </tr>
              </thead>
              <tbody>
                {publications.map(pub => (
                  <tr key={pub.id} className="clickable-row" onClick={() => openDetail(pub)} title="Нажмите, чтобы посмотреть подробности">
                    <td className="title-cell">{pub.title}</td>
                    <td>{pub.author}</td>
                    <td>{pub.year}</td>
                    <td>{pub.department_display}</td>
                    <td>{pub.publication_type_display || '—'}</td>
                    <td>{pub.citation_db_display || '—'}</td>
                    <td>{pub.author_status_display || '—'}</td>
                    {canDelete && (
                      <td>
                        <button
                          className="icon-delete-btn"
                          title="Удалить (в архив)"
                          onClick={(e) => handleSoftDelete(e, pub)}
                        >
                          <Trash2 size={16} />
                        </button>
                      </td>
                    )}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {totalPages > 1 && (
            <div className="pagination">
              <button onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1} aria-label="Предыдущая страница">
                <ChevronLeft size={20} />
              </button>
              <span>Страница {page} из {totalPages}</span>
              <button onClick={() => setPage(p => Math.min(totalPages, p + 1))} disabled={page === totalPages} aria-label="Следующая страница">
                <ChevronRight size={20} />
              </button>
            </div>
          )}
        </>
      )}

      {selectedId && (
        <div className="detail-overlay" onClick={closeDetail}>
          <div className="detail-modal" onClick={(e) => e.stopPropagation()}>
            <div className="detail-modal-header">
              <div>
                <h3>Карточка публикации</h3>
                <span className="detail-modal-sub">№ {detail?.id ?? selectedId}</span>
              </div>
              <button className="detail-close" onClick={closeDetail} aria-label="Закрыть">
                <X size={22} />
              </button>
            </div>

            <div className="detail-modal-body">
              {detailLoading || !detail ? (
                <div className="loading">
                  <div className="spinner" />
                  <span>Загрузка данных...</span>
                </div>
              ) : (
                <>
                  <h2 className="detail-title">{detail.title}</h2>

                  <div className="detail-badges">
                    <span className={`badge ${detectStatusBadge(detail)}`}>{detail.status_display}</span>
                    <span className={`badge ${detectModerationBadge(detail.moderation_status)}`}>
                      {detail.moderation_status_display}
                    </span>
                  </div>

                  <DetailSection title="Основные сведения">
                    <Field label="Автор(ы)" value={detail.author} full />
                    <Field label="Год" value={detail.year} />
                    <Field label="Кафедра" value={detail.department_display} />
                    <Field label="Тип публикации" value={detail.publication_type_display} />
                    <Field label="Вид публикации" value={detail.publication_scope_display} />
                    <Field label="Результат" value={detail.result_display} />
                  </DetailSection>

                  <DetailSection title="Руководитель и исполнители">
                    <Field label="Руководитель" value={detail.head} />
                    <Field label="Исполнители" value={detail.executors} />
                    <Field label="Студенты" value={detail.students_names} />
                    <Field label="Количество студентов" value={detail.students_count} />
                  </DetailSection>

                  <DetailSection title="Мероприятие / издание">
                    <Field label="Название события / издания" value={detail.event_name} />
                    <Field label="Место проведения" value={detail.location} />
                    <Field label="Дата проведения" value={formatDate(detail.event_date)} />
                    <Field label="База цитирования" value={detail.citation_db_display} />
                    <Field label="Статус автора" value={detail.author_status_display} />
                  </DetailSection>

                  <DetailSection title="Объём издания">
                    <Field label="Количество страниц" value={detail.pages_count} />
                    <Field label="Печатные листы" value={detail.printed_sheets} />
                    <Field label="Тираж" value={detail.circulation} />
                    <Field label="Том / выпуск" value={detail.volume} />
                  </DetailSection>

                  <DetailSection title="Идентификаторы">
                    <Field label="DOI" value={detail.doi} />
                    <Field label="EDN" value={detail.edn_code} />
                    <Field label="ID eLibrary" value={detail.elibrary_id} />
                  </DetailSection>

                  <DetailSection title="Отчётность">
                    <Field label="Отчётный период" value={detail.reporting_period_display} />
                    <Field label="Отчётный год" value={detail.reporting_year} />
                    <Field label="Месяц внесения" value={monthLabel(detail.entry_month)} />
                  </DetailSection>

                  <DetailSection title="Финансирование и примечания">
                    <Field label="Источник финансирования" value={detail.funding_source} />
                    <Field label="Примечание" value={detail.note} full />
                  </DetailSection>

                  <DetailSection title="Служебная информация">
                    <Field label="Владелец" value={ownerName} />
                    <Field label="Комментарий модерации" value={detail.moderation_comment} />
                    <Field label="Модератор" value={moderatorName} />
                    <Field label="Дата модерации" value={formatDate(detail.moderated_at)} />
                    <Field label="В архиве" value={detail.is_archived ? 'Да' : 'Нет'} />
                    <Field label="Создано" value={formatDate(detail.created_at)} />
                    <Field label="Обновлено" value={formatDate(detail.updated_at)} />
                  </DetailSection>
                </>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default PublicWorks