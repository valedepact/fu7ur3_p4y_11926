import { NavLink } from "react-router-dom";

export default function Nav() {
  return (
    <nav className="nav">
      <NavLink to="/" end>Overview</NavLink>
      <NavLink to="/loads">Sales</NavLink>
      <NavLink to="/expenses">Expenses</NavLink>
      <NavLink to="/customers">Customers</NavLink>
      <NavLink to="/item-classes">Services</NavLink>
    </nav>
  );
}