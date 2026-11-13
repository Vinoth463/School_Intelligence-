
import { useState } from "react";
import { Bell, UserCircle, Menu, X } from "lucide-react";
import { Outlet } from "react-router-dom";

import { useAuth } from "../../context/AuthContext";
import Sidebar from "./Sidebar";
import "./AppLayout.css";

export default function AppLayout() {
  const { user } = useAuth();
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  const closeSidebar = () => {
    setIsSidebarOpen(false);
  };

  return (
    <div className="app-layout">
      <div
        className={`sidebar-shell ${isSidebarOpen ? "sidebar-open" : ""}`}
      >
        <Sidebar onNavigate={closeSidebar} />
      </div>

      {isSidebarOpen && (
        <button
          type="button"
          className="sidebar-backdrop"
          aria-label="Close navigation menu"
          onClick={closeSidebar}
        />
      )}

      <div className="app-main">
        <header className="app-header">
          <div className="header-left">
            <button
              type="button"
              className="mobile-menu-button"
              aria-label={isSidebarOpen ? "Close menu" : "Open menu"}
              aria-expanded={isSidebarOpen}
              onClick={() => setIsSidebarOpen((open) => !open)}
            >
              {isSidebarOpen ? <X size={21} /> : <Menu size={21} />}
            </button>

            <div className="header-breadcrumb">
              <span>School Intelligence</span>
              <span className="breadcrumb-separator">/</span>
              <strong>Academic Platform</strong>
            </div>
          </div>

          <div className="header-actions">
            <button
              type="button"
              className="header-icon-button"
              aria-label="Notifications"
            >
              <Bell size={19} />
            </button>

            <div className="header-user">
              <div className="header-user-avatar">
                <UserCircle size={25} />
              </div>

              <div className="header-user-details">
                <strong>{user?.full_name ?? "User"}</strong>
                <span>{user?.role ?? "Account"}</span>
              </div>
            </div>
          </div>
        </header>

        <main className="app-content">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
