import { NavLink } from "react-router-dom";
import {
  LayoutDashboard, Shirt, Receipt, Users, Tags, BarChart3, Truck, Settings as SettingsIcon,
} from "lucide-react";

const NAV_ITEMS = [
  { to: "/", label: "Overview", icon: LayoutDashboard, end: true },
  { to: "/loads", label: "Loads", icon: Shirt },
  { to: "/expenses", label: "Expenses", icon: Receipt },
  { to: "/customers", label: "Customers", icon: Users },
  { to: "/item-classes", label: "Item Classes", icon: Tags },
  { to: "/reports", label: "Reports", icon: BarChart3 },
  { to: "/pickup-requests", label: "Pickup Requests", icon: Truck },
  { to: "/settings", label: "Settings", icon: SettingsIcon },
];

export default function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <span className="logo-mark">De pact</span>
        <span className="logo-tag">We are not selling, we are washing shoes.</span>
      </div>
      <nav className="sidebar-nav">
        {NAV_ITEMS.map(({ to, label, icon: Icon, end }) => (
          <NavLink
            key={to}
            to={to}
            end={end}
            className={({ isActive }) => "sidebar-link" + (isActive ? " active" : "")}
          >
            <Icon size={18} strokeWidth={1.8} />
            <span>{label}</span>
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}