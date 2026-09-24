import { useEffect } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import DashboardLayout from "./components/DashboardLayout";
import Overview from "./pages/Overview";
import Loads from "./pages/Loads";
import Expenses from "./pages/Expenses";
import Customers from "./pages/Customers";
import ItemClasses from "./pages/ItemClasses";
import { startSyncListener } from "./offline/sync";
import "./App.css";
import Reports from "./pages/Reports";
import PickupRequests from "./pages/PickupRequests";
import Settings from "./pages/Settings";

export default function App() {
  useEffect(() => { startSyncListener(); }, []);

  return (
    <BrowserRouter>
      <Routes>
        <Route element={<DashboardLayout />}>
          <Route path="/" element={<Overview />} />
          <Route path="/loads" element={<Loads />} />
          <Route path="/expenses" element={<Expenses />} />
          <Route path="/customers" element={<Customers />} />
          <Route path="/item-classes" element={<ItemClasses />} />
          <Route path="/reports" element={<Reports />} />
          <Route path="/pickup-requests" element={<PickupRequests />} />
          <Route path="/settings" element={<Settings />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}