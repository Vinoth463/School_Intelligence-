
import { NavLink, useNavigate } from "react-router-dom";
import {
  GraduationCap,
  LayoutDashboard,
  ChartNoAxesCombined,
  ClipboardCheck,
  Brain,
  MessageSquare,
  Upload,
  FileText,
  LogOut,
} from "lucide-react";

import { useAuth } from "../../context/AuthContext";
import "./Sidebar.css";

interface SidebarProps {
  onNavigate?: () => void;
}

const navigationItems = [
  {
    label: "Dashboard",
    path: "/dashboard",
    icon: LayoutDashboard,
  },
  {
    label: "Academic Analytics",
    path: "/analytics",
    icon: ChartNoAxesCombined,
  },
  {
    label: "Attendance",
    path: "/attendance",
    icon: ClipboardCheck,
  },
  {
    label: "ML Predictions",
    path: "/predictions",
    icon: Brain,
  },
  {
    label: "AI Assistant",
    path: "/assistant",
    icon: MessageSquare,
  },
  {
    label: "Data Imports",
    path: "/imports",
    icon: Upload,
  },
  {
    label: "Reports",
    path: "/reports",
    icon: FileText,
  },
];

export default function Sidebar({ onNavigate }: SidebarProps) {
  const { logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    onNavigate?.();
    logout();
    navigate("/login", { replace: true });
  };

  return (
    <aside className="app-sidebar">
      <div className="sidebar-brand">
        <div className="sidebar-brand-icon">
          <GraduationCap size={27} />
        </div>

        <div>
          <h2>School Intelligence</h2>
          <span>Academic Platform</span>
        </div>
      </div>

      <div className="sidebar-section-label">MAIN MENU</div>

      <nav className="sidebar-navigation">
        {navigationItems.map((item) => {
          const Icon = item.icon;

          return (
            <NavLink
              key={item.path}
              to={item.path}
              onClick={onNavigate}
              className={({ isActive }) =>
                `sidebar-link ${isActive ? "active" : ""}`
              }
            >
              <Icon size={19} />
              <span>{item.label}</span>
            </NavLink>
          );
        })}
      </nav>

      <div className="sidebar-bottom">
        <button
          type="button"
          className="sidebar-logout"
          onClick={handleLogout}
        >
          <LogOut size={19} />
          <span>Logout</span>
        </button>

        <div className="sidebar-version">
          School Intelligence v1.0
        </div>
      </div>
    </aside>
  );
}
