import React, { useState } from 'react'
import { Outlet, Link, useNavigate, useLocation } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import { useUI } from '../../context/UIProvider'
import {
  Menu, BookOpen, BarChart3, LogIn, LayoutDashboard, ShieldCheck,
  Trash2, User, LogOut, X, UserCircle2
} from 'lucide-react'
import './Layout.css'

const Layout = () => {
  const { user, logout } = useAuth()
  const { openLogin } = useUI()
  const navigate = useNavigate()
  const location = useLocation()

  const [expanded, setExpanded] = useState(true)
  const [drawerOpen, setDrawerOpen] = useState(false)

  const isModerator = user && (user.role === 'ADMIN' || user.role === 'NIO_STAFF')
  const isAdmin = user?.role === 'ADMIN'

  const handleLogout = async () => {
    await logout()
    navigate('/')
    setDrawerOpen(false)
  }

  const closeDrawer = () => setDrawerOpen(false)
  const isActive = (path) => location.pathname === path || location.pathname.startsWith(path + '/')

  const navItems = [
    { path: '/public-works', label: 'Публикации', icon: <LayoutDashboard size={22} />, show: true },
    { path: '/statistics', label: 'Статистика', icon: <BarChart3 size={22} />, show: true },
    { path: '/cabinet', label: 'Кабинет', icon: <UserCircle2 size={22} />, show: !!user },
    { path: '/admin', label: isAdmin ? 'Админ-панель' : 'Модерация', icon: <ShieldCheck size={22} />, show: isModerator },
    { path: '/deleted', label: 'Удалённые', icon: <Trash2 size={22} />, show: isModerator },
  ]

  const visibleNav = navItems.filter(n => n.show)

  const renderNav = () =>
    visibleNav.map(item => (
      <Link
        key={item.path}
        to={item.path}
        className={`nav-item ${isActive(item.path) ? 'active' : ''}`}
        title={expanded ? undefined : item.label}
        onClick={closeDrawer}
      >
        <span className="nav-item-icon">{item.icon}</span>
        {expanded && <span className="nav-item-label">{item.label}</span>}
      </Link>
    ))

  return (
    <div className="layout">
      {/* Desktop / tablet sidebar (persistent or rail) */}
      <aside className={`sidebar ${expanded ? 'sidebar-expanded' : 'sidebar-rail'}`}>
        <div className="sidebar-brand">
          <Link to="/public-works" className="brand-logo" onClick={closeDrawer}>
            <BookOpen size={26} />
            {expanded && <span>База науч.&nbsp;трудов</span>}
          </Link>
        </div>

        <nav className="sidebar-nav">
          {renderNav()}
        </nav>

        <div className="sidebar-footer">
          {user ? (
            <>
              <div className="sidebar-user" title={expanded ? undefined : `${user.first_name} ${user.last_name}`}>
                <span className="sidebar-avatar">
                  {(user.first_name?.[0] || user.username?.[0] || '?').toUpperCase()}
                </span>
                {expanded && (
                  <div className="sidebar-user-text">
                    <span className="sidebar-user-name">{user.first_name} {user.last_name}</span>
                    <span className="sidebar-user-role">{user.role_display || user.role}</span>
                  </div>
                )}
              </div>
              <button className="nav-item nav-logout" onClick={handleLogout} title={expanded ? undefined : 'Выход'}>
                <span className="nav-item-icon"><LogOut size={20} /></span>
                {expanded && <span className="nav-item-label">Выход</span>}
              </button>
            </>
          ) : (
            <button className="nav-item" onClick={openLogin} title={expanded ? undefined : 'Вход'}>
              <span className="nav-item-icon"><LogIn size={20} /></span>
              {expanded && <span className="nav-item-label">Вход</span>}
            </button>
          )}
        </div>

        <button
          className="sidebar-toggle"
          onClick={() => setExpanded(e => !e)}
          title={expanded ? 'Свернуть' : 'Развернуть'}
        >
          {expanded ? <Menu size={18} /> : <Menu size={18} />}
        </button>
      </aside>

      {/* Offcanvas drawer (mobile) */}
      {drawerOpen && <div className="drawer-overlay" onClick={closeDrawer} />}
      <aside className={`drawer ${drawerOpen ? 'drawer-open' : ''}`}>
        <div className="sidebar-brand">
          <Link to="/public-works" className="brand-logo" onClick={() => setDrawerOpen(false)}>
            <BookOpen size={26} />
            <span>База науч.&nbsp;трудов</span>
          </Link>
          <button className="drawer-close" onClick={closeDrawer} aria-label="Закрыть"><X size={22} /></button>
        </div>
        <nav className="sidebar-nav">
          {visibleNav.map(item => (
            <Link
              key={item.path}
              to={item.path}
              className={`nav-item ${isActive(item.path) ? 'active' : ''}`}
              onClick={closeDrawer}
            >
              <span className="nav-item-icon">{item.icon}</span>
              <span className="nav-item-label">{item.label}</span>
            </Link>
          ))}
        </nav>
        <div className="sidebar-footer">
          {user ? (
            <button className="nav-item nav-logout" onClick={handleLogout}>
              <span className="nav-item-icon"><LogOut size={20} /></span>
              <span className="nav-item-label">Выход</span>
            </button>
          ) : (
            <button className="nav-item" onClick={() => { closeDrawer(); openLogin() }}>
              <span className="nav-item-icon"><LogIn size={20} /></span>
              <span className="nav-item-label">Вход</span>
            </button>
          )}
        </div>
      </aside>

      {/* Main column */}
      <div className="layout-main">
        <header className="topbar">
          <button className="hamburger" onClick={() => setDrawerOpen(true)} aria-label="Меню">
            <Menu size={24} />
          </button>
          <div className="topbar-title">
            <BookOpen size={20} />
            <span>База научных трудов</span>
          </div>
          <div className="topbar-user">
            {user ? (
              <>
                <span className="topbar-role">{user.role_display || user.role}</span>
                <span className="topbar-txt">{user.first_name} {user.last_name}</span>
              </>
            ) : (
              <button className="md-btn md-btn-filled" onClick={openLogin}><LogIn size={16} /> Вход</button>
            )}
          </div>
        </header>

        <main className="main">
          <Outlet />
        </main>
      </div>
    </div>
  )
}

export default Layout
