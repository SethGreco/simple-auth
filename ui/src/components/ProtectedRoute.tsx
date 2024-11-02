import React, { useEffect, useState } from "react";
import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "../AuthProvider";

const ProtectedRoute = () => {
  const user = useAuth();
  const [isValid, setIsValid] = useState<boolean | null>(null);

  const validateToken = async () => {
    const url = `http://localhost:8000/login/valid/`;

    const response = await fetch(url, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${user?.token}`,
        "Content-Type": "application/json",
      },
    });
    if (response.status == 200) {
      setIsValid(true);
    } else {
      setIsValid(false);
    }
  };

  useEffect(() => {
    if (user?.token !== null) {
      validateToken();
    }
  }, [user?.token]);

  if (isValid === false) {
    user?.logOut();
    return <Navigate to="/login" replace />;
  }

  return user?.token ? <Outlet /> : <Navigate to="/login" replace />;
};

export default ProtectedRoute;
