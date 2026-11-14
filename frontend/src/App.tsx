
import {
  BrowserRouter,
  Navigate,
  Route,
  Routes,
} from "react-router-dom";

import Login from "./pages/Login/Login";
import Dashboard from "./pages/Dashboard/Dashboard";
import Analytics from "./pages/Analytics/Analytics";
import Predictions from "./pages/Predictions/Predictions";
import Attendance from "./pages/Attendance/Attendance";
import AcademicAssistant from "./pages/Assistant/AcademicAssistant";
import Imports from "./pages/Imports/Imports";
import Reports from "./pages/Reports/Reports";

import ProtectedRoute from "./components/common/ProtectedRoute";
import PublicRoute from "./components/common/PublicRoute";
import AppLayout from "./components/layout/AppLayout";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public routes */}
        <Route element={<PublicRoute />}>
          <Route path="/login" element={<Login />} />
        </Route>

        {/* Protected application routes */}
        <Route element={<ProtectedRoute />}>
          <Route element={<AppLayout />}>
            <Route
              path="/dashboard"
              element={<Dashboard />}
            />

            <Route
              path="/analytics"
              element={<Analytics />}
            />

            <Route
              path="/attendance"
              element={<Attendance />}
            />

            <Route
              path="/predictions"
              element={<Predictions />}
            />

            <Route
              path="/assistant"
              element={<AcademicAssistant />}
            />

            <Route
              path="/imports"
              element={<Imports />}
            />

            <Route
              path="/reports"
              element={<Reports />}
            />
          </Route>
        </Route>

        {/* Default routes */}
        <Route
          path="/"
          element={<Navigate to="/dashboard" replace />}
        />

        <Route
          path="*"
          element={<Navigate to="/dashboard" replace />}
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
