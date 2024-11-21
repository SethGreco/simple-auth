import React, { useEffect, useState } from "react";
import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "../contexts/AuthProvider";

const ProtectedRoute = () => {
  const auth = useAuth();
  const [isValid, setIsValid] = useState<boolean | null>(null);

  const validateToken = () => {
    if (Date.now() < auth?.user?.exp * 1000) {
      setIsValid(true);
    } else {
      setIsValid(false);
    }
  };

  useEffect(() => {
    if (auth?.token !== null) {
      validateToken();
    }
  }, []);

  if (isValid === false) {
    auth?.logOut();
    return <Navigate to="/login" replace />;
  }

  return auth?.token ? <Outlet /> : <Navigate to="/login" replace />;
};

export default ProtectedRoute;
