import { createContext, useContext, useState, useCallback } from 'react'
import { useAuth } from './AuthContext'
import api from '../services/api'
import { LogIn, X } from 'lucide-react'
import '../pages/Login/Login.css'

const UIContext = createContext(undefined)

export function UIProvider({ children }) {
  const [isLoginOpen, setIsLoginOpen] = useState(false)

  const openLogin = useCallback(() => setIsLoginOpen(true), [])
  const closeLogin = useCallback(() => setIsLoginOpen(false), [])

  return (
    <UIContext.Provider value={{ isLoginOpen, openLogin, closeLogin }}>
      {children}
      <LoginModal isOpen={isLoginOpen} onClose={closeLogin} />
    </UIContext.Provider>
  )
}

export function useUI() {
  const context = useContext(UIContext)
  if (context === undefined) {
    throw new Error('useUI must be used within a UIProvider')
  }
  return context
}

const LoginModal = ({ isOpen, onClose }) => {
  const { login } = useAuth()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  if (!isOpen) return null

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setIsLoading(true)

    try {
      await login(username, password)
      setUsername('')
      setPassword('')
      onClose()
    } catch (err) {
      setError(err.response?.data?.error || err.response?.data?.detail || 'Ошибка входа')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="login-overlay" onClick={onClose}>
      <div className="login-card login-modal-card" onClick={(e) => e.stopPropagation()}>
        <button type="button" className="login-close" onClick={onClose} aria-label="Закрыть">
          <X size={20} />
        </button>

        <div className="login-header">
          <div className="login-logo">
            <LogIn size={26} />
          </div>
          <h1>Вход в систему</h1>
          <p>База научных трудов</p>
        </div>

        <form onSubmit={handleSubmit} className="login-form">
          {error && <div className="error-message">{error}</div>}

          <div className="form-group">
            <label htmlFor="username">Логин</label>
            <input
              id="username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Введите логин"
              required
              autoFocus
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Пароль</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Введите пароль"
              required
            />
          </div>

          <button type="submit" className="btn-submit" disabled={isLoading}>
            {isLoading ? 'Вход...' : 'Войти'}
          </button>
        </form>
      </div>
    </div>
  )
}

export default UIProvider