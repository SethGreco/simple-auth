import React, { useContext, createContext, useState, useEffect } from "react";

interface AuthContextProps {
  token: string | null;
  loginAction: (
    username: string,
    password: string
  ) => Promise<number | undefined>;
  logOut: () => void;
  user: UserDetail | null;
}

interface UserDetail {
  sub: string;
  id: number;
  exp: number;
}

const AuthContext = createContext<AuthContextProps | undefined>(undefined);

export const AuthProvider = ({ children }) => {
  const [token, setToken] = useState(null);
  const [user, setUser] = useState(null);

  const url = `http://localhost:8000/login/user/`;

  const loginAction = async (username: string, password: string) => {
    try {
      const response = await fetch(url, {
        method: "POST",
        headers: {
          Authorization: `Basic ${btoa(`${username}:${password}`)}`,
          "Content-Type": "application/json",
        },
      });
      const res = await response.json();
      console.log(res, response);
      if (res.accessToken) {
        setToken(res.accessToken);
        const details = parseJwt(res.accessToken);
        setUser(details);
        return response.status;
      }
      throw new Error(res.message);
    } catch (err) {
      console.error(err);
    }
  };

  const logOut = () => {
    setToken(null);
    setUser(null);
  };

  const contextValue: AuthContextProps = {
    token,
    loginAction,
    logOut,
    user,
  };

  return (
    <AuthContext.Provider value={contextValue}>{children}</AuthContext.Provider>
  );
};

export const useAuth = () => {
  return useContext(AuthContext);
};

const parseJwt: any = (token: string) => {
  var base64Url = token.split(".")[1];
  var base64 = base64Url.replace(/-/g, "+").replace(/_/g, "/");
  var jsonPayload = decodeURIComponent(
    window
      .atob(base64)
      .split("")
      .map(function (c) {
        return "%" + ("00" + c.charCodeAt(0).toString(16)).slice(-2);
      })
      .join("")
  );

  return JSON.parse(jsonPayload);
};
