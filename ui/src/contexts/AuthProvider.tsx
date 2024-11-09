import React, { useContext, createContext, useState, useEffect } from "react";
import { config } from "../config/config";

interface AuthContextProps {
  readonly token: string | null;
  loginAction: (
    username: string,
    password: string
  ) => Promise<number | undefined>;
  logOut: () => void;
  readonly user: UserDetail | null;
}

interface UserDetail {
  readonly sub: string;
  readonly id: number;
  readonly exp: number;
}

const AuthContext = createContext<AuthContextProps | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [token, setToken] = useState<string | null>(null);
  const [user, setUser] = useState<UserDetail | null>(null);

  useEffect(() => {
    const restoreSession = async () => {
      try {
        const valid_url = `${config.backendUrl}/login/refresh`;
        const response = await fetch(valid_url, { credentials: "include" });

        if (response.status === 200) {
          // TODO: log user back in
        } else if (response.status === 401) {
          console.log("handle unauth");
          // TODO: Do nothing ?
        }
      } catch (err) {
        console.log(err);
        throw err;
      }
    };

    restoreSession();
  }, []);

  const loginAction = async (username: string, password: string) => {
    try {
      const url = `${config.backendUrl}/login/user/`;
      const response = await fetch(url, {
        method: "POST",
        headers: {
          Authorization: `Basic ${btoa(`${username}:${password}`)}`,
          "Content-Type": "application/json",
        },
        credentials: "include",
      });
      const res = await response.json();
      if (res.accessToken) {
        setToken(res.accessToken);
        const details = parseJwt(res.accessToken);
        setUser(details);
        return response.status;
      }
      throw new Error(res.message);
    } catch (err) {
      console.error(err);
      return;
    }
  };

  const logOut = async () => {
    const url = `${config.backendUrl}/login/logout`;
    const response = await fetch(url, {
      credentials: "include",
    });
    const res = await response.json();
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
