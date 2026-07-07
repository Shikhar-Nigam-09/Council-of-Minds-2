import { BrowserRouter, Routes, Route } from "react-router-dom";
import Landing from "../pages/Landing";
import Login from "../pages/Login";
import Register from "../pages/Register";
import Documents from "../pages/Documents";
import DocumentDetail from "../pages/DocumentDetail";
import Chat from "../pages/Chat";
import History from "../pages/History";
import Settings from "../pages/Settings";
import ProtectedRoute from "../components/auth/ProtectedRoute";
import AppShell from "../components/layout/AppShell";

export default function AppRouter() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        {/* Protected Application Shell Routes */}
        <Route
          element={
            <ProtectedRoute>
              <AppShell />
            </ProtectedRoute>
          }
        >
          <Route path="/" element={<Landing />} />
          <Route path="/documents" element={<Documents />} />
          <Route path="/documents/:documentId" element={<DocumentDetail />} />
          <Route path="/chat" element={<Chat />} />
          <Route path="/chat/:chatId" element={<Chat />} />
          <Route path="/history" element={<History />} />
          <Route path="/settings" element={<Settings />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
