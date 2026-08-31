import { useState, useEffect } from 'react'
import api from '../../services/api'
import { useToast } from '../../components/Toast'
import { useReferenceData } from '../../services/reference'
import { Plus, Edit, Trash2, Save, Clock, AlertCircle } from 'lucide-react'
import './MethodistCabinet.css'

const defaultValues = {
  title: '',
  author: '',
  year: new Date().getFullYear(),
  department: '',
  result: '',
  publication_type: '',
  publication_scope: '',
  citation_db: '',
  author_status: '',
  reporting_period: '',
  reporting_year: '',
  circulation: '',
  head: '',
  executors: '',
  location: '',
  event_name: '',
  funding_source: '',
  volume: '',
  printed_sheets: '',
  keywords: '',
  doi: '',
  edn_code: '',
  elibrary_id: '',
  note: '',
  students_names: '',
  students_count: 0,
  pages_count: 0,
  entry_month: new Date().getMonth() + 1,
  event_date: '',
}

const MethodistCabinet = () => {
  const { reference } = useReferenceData()
  const [showForm, setShowForm] = useState(false)
  const [editingId, setEditingId] = useState(null)
  const [publications, setPublications] = useState([])
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [formData, setFormData] = useState(defaultValues)
  const [errors, setErrors] = useState({})
  const toast = useToast()

  useEffect(() => {
    loadPublications()
  }, [])

  const loadPublications = async () => {
    try {
      const response = await api.get('/publications/my_publications/?page_size=200')
      setPublications(response.data.results || response.data)
    } catch (error) {
      console.error('Error loading publications:', error)
      toast.addToast({
        type: 'error',
        title: 'Ошибка загрузки',
        message: 'Не удалось загрузить список публикаций. Попробуйте обновить страницу.'
      })
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    const newErrors = {}

    if (!formData.title.trim()) newErrors.title = 'Обязательное поле'
    if (!formData.author.trim()) newErrors.author = 'Обязательное поле'

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors)
      toast.addToast({
        type: 'error',
        title: 'Ошибка валидации',
        message: 'Пожалуйста, заполните все обязательные поля'
      })
      return
    }

    setSaving(true)
    try {
      const currentYear = new Date().getFullYear()
      const submitData = {
        ...formData,
        year: Number(formData.year) || currentYear,
        event_date: formData.event_date || null,
        printed_sheets: formData.printed_sheets === '' || formData.printed_sheets == null
          ? 0
          : (Number(formData.printed_sheets) || 0),
        circulation: formData.circulation === '' || formData.circulation == null
          ? 0
          : (Number(formData.circulation) || 0),
        students_count: Number(formData.students_count) || 0,
        pages_count: Number(formData.pages_count) || 0,
        entry_month: Number(formData.entry_month) || new Date().getMonth() + 1,
      }
      delete submitData.departments
      delete submitData.keywords

      let response
      if (editingId) {
        response = await api.patch(`/publications/${editingId}/`, submitData)
      } else {
        response = await api.post('/publications/', submitData)
      }

      await loadPublications()

      toast.addToast({
        type: 'success',
        title: editingId ? 'Запись обновлена' : 'Запись создана',
        message: 'Запись успешно сохранена и направлена на модерацию для проверки.',
        duration: 6000
      })

      setShowForm(false)
      setEditingId(null)
      setFormData(defaultValues)
      setErrors({})
    } catch (error) {
      console.error('Error saving publication:', error)

      const validationErrors = error.response?.data
      if (validationErrors) {
        const parsedErrors = {}

        if (validationErrors.non_field_errors) {
          parsedErrors.general = Array.isArray(validationErrors.non_field_errors)
            ? validationErrors.non_field_errors.join('. ')
            : validationErrors.non_field_errors
        }

        Object.keys(validationErrors).forEach(key => {
          if (key !== 'non_field_errors' && key !== 'detail') {
            const value = validationErrors[key]
            parsedErrors[key] = Array.isArray(value) ? value.join('. ') : String(value)
          }
        })

        if (Object.keys(parsedErrors).length === 0 && validationErrors.detail) {
          parsedErrors.general = validationErrors.detail
        }

        setErrors(parsedErrors)

        toast.addToast({
          type: 'error',
          title: 'Ошибка сохранения',
          message: 'Проверьте правильность заполнения полей'
        })
      } else {
        toast.addToast({
          type: 'error',
          title: 'Ошибка сети',
          message: 'Не удалось сохранить запись. Проверьте подключение к интернету.'
        })
      }
    } finally {
      setSaving(false)
    }
  }

  const handleEdit = (pub) => {
    setEditingId(pub.id)
    setShowForm(true)
    setFormData({
      title: pub.title || '',
      author: pub.author || '',
      year: pub.year || new Date().getFullYear(),
      department: pub.department || '',
      result: pub.result || '',
      publication_type: pub.publication_type || '',
      publication_scope: pub.publication_scope || '',
      citation_db: pub.citation_db || '',
      author_status: pub.author_status || '',
      reporting_period: pub.reporting_period || '',
      reporting_year: pub.reporting_year || '',
      circulation: pub.circulation || '',
      head: pub.head || '',
      executors: pub.executors || '',
      location: pub.location || '',
      event_name: pub.event_name || '',
      funding_source: pub.funding_source || '',
      volume: pub.volume || '',
      printed_sheets: pub.printed_sheets || '',
      keywords: pub.keywords || '',
      doi: pub.doi || '',
      edn_code: pub.edn_code || '',
      elibrary_id: pub.elibrary_id || '',
      note: pub.note || '',
      students_names: pub.students_names || '',
      students_count: pub.students_count || 0,
      pages_count: pub.pages_count || 0,
      entry_month: pub.entry_month || new Date().getMonth() + 1,
      event_date: pub.event_date || '',
    })
    setErrors({})
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Вы уверены, что хотите удалить эту запись? Запись будет архивирована.')) return

    try {
      await api.delete(`/publications/${id}/`)
      toast.addToast({
        type: 'success',
        title: 'Запись удалена',
        message: 'Запись перемещена в архив.'
      })
      await loadPublications()
    } catch (error) {
      console.error('Error deleting publication:', error)
      toast.addToast({
        type: 'error',
        title: 'Ошибка удаления',
        message: 'Не удалось удалить запись. Возможно, запись уже в архиве.'
      })
    }
  }

  const handleCancel = () => {
    setShowForm(false)
    setEditingId(null)
    setFormData(defaultValues)
    setErrors({})
  }

  const handleInputChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }))
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }))
    }
  }

  const departments = reference?.departments || []
  const publicationTypes = reference?.publication_types || []
  const publicationScopes = reference?.publication_scopes || []
  const citationDatabases = reference?.citation_databases || []
  const authorStatuses = reference?.author_statuses || []
  const reportingPeriods = reference?.reporting_periods || []
  const results = reference?.results || []
  const months = reference?.months || []

  return (
    <div className="cabinet">
      <div className="cabinet-header">
        <h1>Кабинет методиста</h1>
        <button className="btn-add" onClick={() => setShowForm(!showForm)}>
          <Plus size={20} />
          {showForm ? 'Отмена' : 'Добавить запись'}
        </button>
      </div>

      {showForm && (
        <div className="form-card">
          <h2>{editingId ? 'Редактирование записи' : 'Новая запись'}</h2>
          <form onSubmit={handleSubmit} className="publication-form">
            {errors.general && <div className="error-banner">{errors.general}</div>}
            {Object.keys(errors).filter(k => k !== 'general').length > 0 && (
              <div className="error-banner field-errors">
                <strong>Проверьте правильность заполнения следующих полей:</strong>
                <ul>
                  {Object.keys(errors).filter(k => k !== 'general').map(k => (
                    <li key={k}>{errors[k]}</li>
                  ))}
                </ul>
              </div>
            )}

            <div className="form-section">
              <h3>Основная информация</h3>
              <div className="form-row">
                <div className="form-group full-width">
                  <label>Название публикации/мероприятия *</label>
                  <input
                    type="text"
                    value={formData.title}
                    onChange={(e) => handleInputChange('title', e.target.value)}
                    className={errors.title ? 'error' : ''}
                  />
                  {errors.title && <span className="error-text">{errors.title}</span>}
                </div>
              </div>

              <div className="form-row">
                <div className="form-group full-width">
                  <label>Автор(ы) *</label>
                  <input
                    type="text"
                    value={formData.author}
                    onChange={(e) => handleInputChange('author', e.target.value)}
                    className={errors.author ? 'error' : ''}
                  />
                  {errors.author && <span className="error-text">{errors.author}</span>}
                </div>
              </div>

              <div className="form-row three-cols">
                <div className="form-group">
                  <label>Год *</label>
                  <input
                    type="number"
                    value={formData.year}
                    onChange={(e) => handleInputChange('year', e.target.value === '' ? '' : parseInt(e.target.value, 10))}
                    min={1900}
                    max={new Date().getFullYear()}
                    className={errors.year ? 'error' : ''}
                  />
                  {errors.year && <span className="error-text">{errors.year}</span>}
                </div>
                <div className="form-group">
                  <label>Кафедра</label>
                  <select
                    value={formData.department}
                    onChange={(e) => handleInputChange('department', e.target.value)}
                  >
                    <option value="">Не указана</option>
                    {departments.map(d => <option key={d.code} value={d.code}>{d.label}</option>)}
                  </select>
                </div>
                <div className="form-group">
                  <label>Результат</label>
                  <select value={formData.result} onChange={(e) => handleInputChange('result', e.target.value)}>
                    <option value="">Не указан</option>
                    {results.map(r => <option key={r.code} value={r.code}>{r.label}</option>)}
                  </select>
                </div>
              </div>

              <div className="form-row two-cols">
                <div className="form-group">
                  <label>Месяц внесения</label>
                  <select value={formData.entry_month} onChange={(e) => handleInputChange('entry_month', parseInt(e.target.value))}>
                    {months.map(m => <option key={m.code} value={m.code}>{m.label}</option>)}
                  </select>
                </div>
                <div className="form-group">
                  <label>Дата проведения</label>
                  <input
                    type="date"
                    value={formData.event_date}
                    onChange={(e) => handleInputChange('event_date', e.target.value)}
                  />
                </div>
              </div>
            </div>

            <div className="form-section">
              <h3>Тип и статус</h3>
              <div className="form-row three-cols">
                <div className="form-group">
                  <label>Тип публикации</label>
                  <select value={formData.publication_type} onChange={(e) => handleInputChange('publication_type', e.target.value)}>
                    <option value="">Не выбран</option>
                    {publicationTypes.map(t => <option key={t.code} value={t.code}>{t.label}</option>)}
                  </select>
                </div>
                <div className="form-group">
                  <label>Уровень публикации</label>
                  <select value={formData.publication_scope} onChange={(e) => handleInputChange('publication_scope', e.target.value)}>
                    <option value="">Не выбран</option>
                    {publicationScopes.map(s => <option key={s.code} value={s.code}>{s.label}</option>)}
                  </select>
                </div>
                <div className="form-group">
                  <label>База цитирования</label>
                  <select value={formData.citation_db} onChange={(e) => handleInputChange('citation_db', e.target.value)}>
                    <option value="">Не выбрана</option>
                    {citationDatabases.map(c => <option key={c.code} value={c.code}>{c.label}</option>)}
                  </select>
                </div>
              </div>

              <div className="form-row three-cols">
                <div className="form-group">
                  <label>Статус автора</label>
                  <select value={formData.author_status} onChange={(e) => handleInputChange('author_status', e.target.value)}>
                    <option value="">Не выбран</option>
                    {authorStatuses.map(s => <option key={s.code} value={s.code}>{s.label}</option>)}
                  </select>
                </div>
                <div className="form-group">
                  <label>Отчётный период</label>
                  <select value={formData.reporting_period} onChange={(e) => handleInputChange('reporting_period', e.target.value)}>
                    <option value="">Не выбран</option>
                    {reportingPeriods.map(p => <option key={p.code} value={p.code}>{p.label}</option>)}
                  </select>
                </div>
                <div className="form-group">
                  <label>Отчётный год</label>
                  <input
                    type="text"
                    value={formData.reporting_year}
                    onChange={(e) => handleInputChange('reporting_year', e.target.value)}
                    placeholder="напр. 2024"
                    className={errors.reporting_year ? 'error' : ''}
                  />
                  {errors.reporting_year && <span className="error-text">{errors.reporting_year}</span>}
                </div>
              </div>
            </div>

            <div className="form-section">
              <h3>Дополнительная информация</h3>
              <div className="form-row two-cols">
                <div className="form-group">
                  <label>Руководитель</label>
                  <input type="text" value={formData.head} onChange={(e) => handleInputChange('head', e.target.value)} />
                </div>
                <div className="form-group">
                  <label>Исполнители</label>
                  <input type="text" value={formData.executors} onChange={(e) => handleInputChange('executors', e.target.value)} />
                </div>
              </div>

              <div className="form-row two-cols">
                <div className="form-group">
                  <label>Место проведения</label>
                  <input type="text" value={formData.location} onChange={(e) => handleInputChange('location', e.target.value)} />
                </div>
                <div className="form-group">
                  <label>Название мероприятия</label>
                  <input type="text" value={formData.event_name} onChange={(e) => handleInputChange('event_name', e.target.value)} />
                </div>
              </div>

              <div className="form-row three-cols">
                <div className="form-group">
                  <label>Тираж</label>
                  <input type="text" value={formData.circulation} onChange={(e) => handleInputChange('circulation', e.target.value)} />
                </div>
                <div className="form-group">
                  <label>Объём</label>
                  <input type="text" value={formData.volume} onChange={(e) => handleInputChange('volume', e.target.value)} placeholder="напр. 5 п.л." />
                </div>
                <div className="form-group">
                  <label>Объём в печатных листах</label>
                  <input
                    type="number"
                    step="0.01"
                    min="0"
                    value={formData.printed_sheets}
                    onChange={(e) => handleInputChange('printed_sheets', e.target.value)}
                    className={errors.printed_sheets ? 'error' : ''}
                  />
                  {errors.printed_sheets && <span className="error-text">{errors.printed_sheets}</span>}
                </div>
              </div>

              <div className="form-row two-cols">
                <div className="form-group">
                  <label>Источник финансирования</label>
                  <input type="text" value={formData.funding_source} onChange={(e) => handleInputChange('funding_source', e.target.value)} />
                </div>
                <div className="form-group">
                  <label>Ключевые слова</label>
                  <input type="text" value={formData.keywords} onChange={(e) => handleInputChange('keywords', e.target.value)} />
                </div>
              </div>

              <div className="form-row three-cols">
                <div className="form-group">
                  <label>DOI</label>
                  <input
                    type="text"
                    value={formData.doi}
                    onChange={(e) => handleInputChange('doi', e.target.value)}
                    placeholder="10.xxxx/xxxx"
                    className={errors.doi ? 'error' : ''}
                  />
                  {errors.doi && <span className="error-text">{errors.doi}</span>}
                </div>
                <div className="form-group">
                  <label>EDN</label>
                  <input
                    type="text"
                    value={formData.edn_code}
                    onChange={(e) => handleInputChange('edn_code', e.target.value)}
                    placeholder="6 заглавных букв или цифр"
                    className={errors.edn_code ? 'error' : ''}
                  />
                  {errors.edn_code && <span className="error-text">{errors.edn_code}</span>}
                </div>
                <div className="form-group">
                  <label>ELibrary ID</label>
                  <input
                    type="text"
                    value={formData.elibrary_id}
                    onChange={(e) => handleInputChange('elibrary_id', e.target.value)}
                    className={errors.elibrary_id ? 'error' : ''}
                  />
                  {errors.elibrary_id && <span className="error-text">{errors.elibrary_id}</span>}
                </div>
              </div>
            </div>

            <div className="form-section">
              <h3>Студенты</h3>
              <div className="form-row three-cols">
                <div className="form-group">
                  <label>Количество студентов</label>
                  <input
                    type="number"
                    value={formData.students_count}
                    onChange={(e) => handleInputChange('students_count', parseInt(e.target.value) || 0)}
                    min={0}
                  />
                </div>
                <div className="form-group">
                  <label>Количество страниц</label>
                  <input
                    type="number"
                    value={formData.pages_count}
                    onChange={(e) => handleInputChange('pages_count', parseInt(e.target.value) || 0)}
                    min={0}
                  />
                </div>
              </div>
              <div className="form-row">
                <div className="form-group full-width">
                  <label>ФИО студентов</label>
                  <textarea
                    value={formData.students_names}
                    onChange={(e) => handleInputChange('students_names', e.target.value)}
                    rows={2}
                    placeholder="Укажите ФИО студентов, принимавших участие"
                  />
                </div>
              </div>
            </div>

            <div className="form-section">
              <h3>Примечания</h3>
              <div className="form-row">
                <div className="form-group full-width">
                  <label>Примечание</label>
                  <textarea
                    value={formData.note}
                    onChange={(e) => handleInputChange('note', e.target.value)}
                    rows={3}
                  />
                </div>
              </div>
            </div>

            <div className="form-actions">
              <button type="button" className="btn-cancel" onClick={handleCancel}>
                Отмена
              </button>
              <button type="submit" className="btn-save" disabled={saving}>
                <Save size={18} />
                {saving ? 'Сохранение...' : 'Сохранить'}
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="publications-list">
        <h2>Мои записи ({publications.length})</h2>

        {loading ? (
          <div className="loading">Загрузка...</div>
        ) : (
          <div className="cards-grid">
            {publications.map(pub => {
              const isRejected = pub.moderation_status === 'rejected'
              const isPendingModeration = pub.moderation_status === 'pending'

              return (
                <div key={pub.id} className={`pub-card ${pub.status} ${isPendingModeration ? 'pending-moderation' : ''}`}>
                  <div className="pub-header">
                    <div className="status-badges">
                      <span className={`status-badge ${pub.status}`}>{pub.status_display}</span>
                      {isPendingModeration && (
                        <span className="status-badge moderation-pending" title="Запись на модерации">
                          <Clock size={12} />
                          На модерации
                        </span>
                      )}
                      {isRejected && pub.moderation_comment && (
                        <span className="status-badge moderation-rejected" title={pub.moderation_comment}>
                          <AlertCircle size={12} />
                          Отклонено
                        </span>
                      )}
                    </div>
                    <div className="pub-actions">
                      <button onClick={() => handleEdit(pub)} title="Редактировать" disabled={isPendingModeration}>
                        <Edit size={16} />
                      </button>
                      <button onClick={() => handleDelete(pub.id)} title="Удалить" className="delete">
                        <Trash2 size={16} />
                      </button>
                    </div>
                  </div>
                  <h3>{pub.title}</h3>
                  <p className="author">{pub.author}</p>
                  <div className="pub-meta">
                    <span>{pub.year}</span>
                    <span>{pub.department_display || pub.department}</span>
                    {pub.result_display && <span className="result">{pub.result_display}</span>}
                  </div>
                  <p className="date">
                    Создано: {new Date(pub.created_at).toLocaleDateString()}
                    {pub.updated_at && pub.updated_at !== pub.created_at && (
                      <span className="updated"> • Обновлено: {new Date(pub.updated_at).toLocaleDateString()}</span>
                    )}
                  </p>
                  {isPendingModeration && (
                    <div className="moderation-notice">
                      <Clock size={14} />
                      <span>Запись направлена на модерацию и ожидает рассмотрения администратором или сотрудником НИО</span>
                    </div>
                  )}
                  {isRejected && pub.moderation_comment && (
                    <div className="moderation-notice rejected">
                      <AlertCircle size={14} />
                      <span>Причина отклонения: {pub.moderation_comment}</span>
                    </div>
                  )}
                </div>
              )
            })}
            {publications.length === 0 && (
              <p className="empty-message">У вас пока нет записей</p>
            )}
          </div>
        )}
      </div>
    </div>
  )
}

export default MethodistCabinet