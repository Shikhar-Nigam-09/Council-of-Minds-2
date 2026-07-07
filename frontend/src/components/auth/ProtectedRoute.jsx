/* eslint-disable react/prop-types */
import { Navigate, useLocation } from "react-router-dom";
import { useAuthStore } from "../../store/authStore";

export default function ProtectedRoute({ children }) {
  const { isAuthenticated, accessToken } = useAuthStore();
  const location = useLocation();

  if (!isAuthenticated || !accessToken) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return children;
}
