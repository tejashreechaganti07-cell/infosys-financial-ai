import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { ProtectedRoute } from './components/layout/ProtectedRoute';
import { Layout } from './components/layout/Layout';
import { DashShell } from './components/dashboard/DashShell';
import { Login } from './pages/Login';
import { Register } from './pages/Register';
import { Landing } from './pages/Landing';
import { Dashboard } from './pages/Dashboard';
import { Workspace } from './pages/Workspace';
import { Reports } from './pages/Reports';
import { Profile } from './pages/Profile';

export function App() {
  return (
    <AuthProvider>
      <BrowserRouter basename={import.meta.env.BASE_URL}>
        <Routes>
          {/* Public entry experience */}
          <Route path="/" element={<Landing />} />

          {/* Public Authentication Routes */}
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />

          {/* Dashboard command center — light shell, same protection */}
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <DashShell>
                  <Dashboard />
                </DashShell>
              </ProtectedRoute>
            }
          />

          {/* Protected Application Workspace Routes */}
          <Route
            element={
              <ProtectedRoute>
                <Layout />
              </ProtectedRoute>
            }
          >
            <Route path="workspace" element={<Workspace />} />
            <Route path="reports" element={<Reports />} />
            <Route path="profile" element={<Profile />} />
          </Route>


          <Route path="*" element={<Navigate to="/" replace />} />

        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
