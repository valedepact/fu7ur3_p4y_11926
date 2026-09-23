export default function TopBar({ title, subtitle }) {
  return (
    <header className="topbar">
      <div>
        <h1>{title}</h1>
        {subtitle && <p className="topbar-subtitle">{subtitle}</p>}
      </div>
      <div className="role-badge">
        <span className="avatar-dot" />
        Manager
      </div>
    </header>
  );
}