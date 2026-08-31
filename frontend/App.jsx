import { Routes, Route, Navigate, useLocation } from 'react-router-dom'
import { useEffect } from 'react'
import { useAuth } from './context/AuthContext'
import { useUI } from './context/UIProvider'
import PublicWorks from './pages/PublicWorks/PublicWorks'
import Statistics from './pages/Statistics/Statistics'
import AdminPanel from './pages/AdminPanel/AdminPanel'
import DeletedRecords from './pages/DeletedRecords/DeletedRecords'
import MethodistCabinet from './pages/MethodistCabinet/MethodistCabinet'
import Layout from './components/Layout/Layout'
import ToastProvider from './components/Toast'
import UIProvider from './context/UIProvider'

const ProtectedRoute = ({ children }) => {
  const { user } = useAuth()
  const { openLogin } = useUI()
  const location = useLocation()

  useEffect(() => {
    if (!user) {
      openLogin()
    }
  }, [user, openLogin])

  if (!user) {
    return <Navigate to="/" replace state={{ from: location.pathname }} />
  }

  return <>{children}</>
}

const App = () => {
  return (
    <ToastProvider>
      <UIProvider>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<Navigate to="/public-works" replace />} />
            <Route path="public-works" element={<PublicWorks />} />
            <Route path="statistics" element={<Statistics />} />
            <Route
              path="admin"
              element={
                <ProtectedRoute>
                  <AdminPanel />
                </ProtectedRoute>
              }
            />
            <Route
              path="deleted"
              element={
                <ProtectedRoute>
                  <DeletedRecords />
                </ProtectedRoute>
              }
            />
            <Route
              path="cabinet"
              element={
                <ProtectedRoute>
                  <MethodistCabinet />
                </ProtectedRoute>
              }
            />
          </Route>
        </Routes>
      </UIProvider>
    </ToastProvider>
  )
}

export default App