import React from 'react';
import '../styles/AppShell.css';

export function AppShell({ children }) {
  return (
    <div className="app-container">
      {children}
    </div>
  );
}

export function AppHeader({ title, subtitle }) {
  return (
    <header className="app-header">
      <div className="app-header-content">
        <div>
          <h1 className="app-title">{title}</h1>
          {subtitle && <p className="app-subtitle">{subtitle}</p>}
        </div>
      </div>
    </header>
  );
}

export function AppSidebar({ children }) {
  const [isOpen, setIsOpen] = React.useState(true);

  return (
    <aside className={`app-sidebar ${isOpen ? 'open' : 'closed'}`}>
      <button
        className="sidebar-toggle"
        onClick={() => setIsOpen(!isOpen)}
      >
        ☰
      </button>
      <nav className="sidebar-nav">
        {children}
      </nav>
    </aside>
  );
}

export function AppMain({ children }) {
  return (
    <main className="app-main">
      {children}
    </main>
  );
}
