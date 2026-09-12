import { BrowserRouter, Routes, Route } from "react-router-dom";
import { useEffect } from "react";
import { startSyncListener } from "./offline/sync";
import Nav from "./components/Nav";
import Overview from "./pages/Overview";
import Loads from "./pages/Loads";
import Expenses from "./pages/Expenses";
import Customers from "./pages/Customers";
import ItemClasses from "./pages/ItemClasses";
import "./App.css";

export default function App() {
  useEffect(() => { startSyncListener(); }, []);
  return (
    <BrowserRouter>
      <div className="dashboard">
        <Nav />
        <Routes>
          <Route path="/" element={<Overview />} />
          <Route path="/loads" element={<Loads />} />
          <Route path="/expenses" element={<Expenses />} />
          <Route path="/customers" element={<Customers />} />
          <Route path="/item-classes" element={<ItemClasses />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}