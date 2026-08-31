import { useState, useEffect } from 'react'
import api from '../../services/api'
import { useToast } from '../../components/Toast'
import { useAuth } from '../../context/AuthContext'
import { Trash2, RotateCcw, Inbox, ChevronLeft, ChevronRight } from 'lucide-react'
import './DeletedRecords.css'

const PAGE_SIZE = 20

const DeletedRecords = () => {
  const { user } = useAuth()
  const toast = useToast()
  const isAdmin = user?.role === 'ADMIN'

  const [records, setRecords] = useState([])
  const [loading, setLoading] = useState(true)
  const [page, setPage] = useState(1)
  const [hasMore, setHasMore] = useState(false)
  const [total, setTotal] = useState(0)
  const [busy, setBusy] = useState(null)

  const load = async () => {
    setLoading(true)
    try {
      const res = await api.get(`/publications/deleted/?page=${page}&page_size=${PAGE_SIZE}`)
      const data = res.data
      setRecords(data.results || data || [])
      setTotal(data.count || 0)
      setHasMore(!!data.next)
    } catch (e) {
      console.error(e)
      toast.addToast({ type: 'error', title: 'Ошибка', message: 'Не удалось загрузить удалённые записи' })
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [page])

  const restore = async (id) => {
    setBusy(id)
    try {
      await api.post(`/publications/${id}/restore/`)
      toast.addToast({ type: 'success', title: 'Восстановлено', message: 'Запись возвращена в активные.' })
      await load()
    } catch (e) {
      toast.addToast({ type: 'error', title: 'Ошибка', message: 'Не удалось восстановить запись' })
    } finally { setBusy(null) }
  }

  const hardDelete = async (id) => {
    if (!window.confirm('Безвозвратно удалить запись из базы? Это действие нельзя отменить.')) return
    setBusy(id)
    try {
      await api.post(`/publications/${id}/hard_delete/`)
      toast.addToast({ type: 'success', title: 'Удалено', message: 'Запись удалена из базы безвозвратно.' })
      await load()
    } catch (e) {
      toast.addToast({ type: 'error', title: 'Ошибка', message: 'Не удалось удалить запись' })
    } finally { setBusy(null) }
  }

  return (
    <div className="deleted-records">
      <div className="page-header">
        <h1>Удалённые записи</h1>
        <p className="subtitle">
          Записи, перемещённые в архив. Здесь их можно восстановить или безвозвратно удалить.
        </p>
      </div>

      {loading ? (
        <div className="loading"><span className="spinner" /> Загрузка...</div>
      ) : records.length === 0 ? (
        <div className="empty-state">
          <Inbox size={56} />
          <p>Нет удалённых записей</p>
          <span className="empty-hint">Записи появятся здесь после мягкого удаления.</span>
        </div>
      ) : (
        <>
          <div className="deleted-summary">Всего в архиве: <strong>{total}</strong></div>
          <div className="cards-grid">
            {records.map(pub => (
              <div key={pub.id} className="md-card pub-card deleted-card">
                <div className="pub-header">
                  <span className="status-badge deleted"><Trash2 size={13} /> В архиве</span>
                  <span className="date">{new Date(pub.created_at).toLocaleDateString()}</span>
                </div>
                <h3>{pub.title}</h3>
                <p className="author">{pub.author}</p>
                <div className="pub-meta">
                  <span>{pub.year}</span>
                  <span>{pub.department_display || pub.department || '—'}</span>
                  <span>{pub.owner_username || '—'}</span>
                </div>
                <div className="deleted-actions">
                  <button
                    className="md-btn md-btn-tonal"
                    onClick={() => restore(pub.id)}
                    disabled={busy === pub.id}
                  >
                    <RotateCcw size={16} /> Восстановить
                  </button>
                  {isAdmin && (
                    <button
                      className="md-btn md-btn-danger"
                      onClick={() => hardDelete(pub.id)}
                      disabled={busy === pub.id}
                    >
                      <Trash2 size={16} /> Удалить
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>

          {total > PAGE_SIZE && (
            <div className="pagination">
              <button
                className="md-btn md-btn-outlined"
                disabled={page <= 1}
                onClick={() => setPage(p => p - 1)}
              >
                <ChevronLeft size={16} /> Назад
              </button>
              <span className="page-info">Стр. {page}</span>
              <button
                className="md-btn md-btn-outlined"
                disabled={!hasMore}
                onClick={() => setPage(p => p + 1)}
              >
                Вперёд <ChevronRight size={16} />
              </button>
            </div>
          )}
        </>
      )}
    </div>
  )
}

export default DeletedRecords
