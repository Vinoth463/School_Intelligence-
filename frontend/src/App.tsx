
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

import ProtectedRoute from "./components/common/ProtectedRoute";
import PublicRoute from "./components/common/PublicRoute";
import PlaceholderPage from "./components/common/PlaceholderPage";
import AppLayout from "./components/layout/AppLayout";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public routes */}
        <Route element={<PublicRoute />}>
          <Route path="/login" element={<Login />} />
        </Route>

        {/* Protected routes with shared application layout */}
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
              element={
                <PlaceholderPage
                  title="Attendance Management"
                  description="Monitor student attendance and identify attendance patterns."
                />
              }
            />

            {/* ML Predictions */}
            <Route
              path="/predictions"
              element={<Predictions />}
            />

            <Route
              path="/assistant"
              element={
                <PlaceholderPage
                  title="AI Assistant"
                  description="Ask questions about your school's academic data."
                />
              }
            />

            <Route
              path="/imports"
              element={
                <PlaceholderPage
                  title="Data Imports"
                  description="Import and manage school academic datasets."
                />
              }
            />

            <Route
              path="/reports"
              element={
                <PlaceholderPage
                  title="Reports"
                  description="View and export academic performance reports."
                />
              }
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
