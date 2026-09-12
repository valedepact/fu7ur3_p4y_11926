import { NavLink } from "react-router-dom";

export default function Nav() {
  return (
    <nav className="nav">
      <NavLink to="/" end>Overview</NavLink>
      <NavLink to="/loads">Loads</NavLink>
      <NavLink to="/expenses">Expenses</NavLink>
      <NavLink to="/customers">Customers</NavLink>
      <NavLink to="/item-classes">Item classes</NavLink>
    </nav>
  );
}