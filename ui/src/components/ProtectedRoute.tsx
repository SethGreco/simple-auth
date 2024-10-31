import React from "react";

import { Navigate, Outlet } from "react-router-dom";
import { getAuthToken } from "../services/authService";

const ProtectedRoute = () => {
  // TODO: Use authentication token
  const localStorageToken = getAuthToken();
  return localStorageToken ? <Outlet /> : <Navigate to="/login" replace />;
};

export default ProtectedRoute;
