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
  const [refreshTimeout, setRefreshTimeout] = useState<NodeJS.Timeout | null>(
    null
  );

  useEffect(() => {
    const refresh = async () => {
      await restoreSession();
    };
    refresh();
    return () => {
      if (refreshTimeout) clearTimeout(refreshTimeout);
    };
  }, []);

  const restoreSession = async () => {
    try {
      const valid_url = `${config.backendUrl}/auth/refresh`;
      const response = await fetch(valid_url, { credentials: "include" });
      const res = await response.json();

      if (response.status === 200) {
        setToken(res.accessToken);
        const details: UserDetail = parseJwt(res.accessToken);
        setUser(details);
        scheduleTokenRefresh(details.exp);
      } else if (response.status === 401) {
        console.log("handle unauth");
        // TODO: handle this
      }
    } catch (err) {
      console.log("this is the error", err);
      throw err;
    }
  };

  const scheduleTokenRefresh = (exp: number) => {
    if (refreshTimeout) clearTimeout(refreshTimeout);
    const expirationTimeMs = exp * 1000;
    // 30 seconds before access token expires
    const timerMs = expirationTimeMs - Date.now() - 30000;
    if (timerMs > 0) {
      const timeId = setTimeout(async () => {
        await restoreSession();
      }, timerMs);
      setRefreshTimeout(timeId);
    }
  };

  const loginAction = async (username: string, password: string) => {
    try {
      const url = `${config.backendUrl}/auth/login`;
      const response = await fetch(url, {
        method: "POST",
        headers: {
          // Authorization: `Basic ${btoa(`${username}:${password}`)}`,
          "Content-Type": "application/x-www-form-urlencoded",
        },
        credentials: "include",
        body: new URLSearchParams({
          username,
          password,
        }),
      });
      const res = await response.json();
      if (res.accessToken) {
        setToken(res.accessToken);
        const details = parseJwt(res.accessToken);
        setUser(details);
        scheduleTokenRefresh(details.exp);
        return response.status;
      }
      throw new Error(res.message);
    } catch (err) {
      console.error(err);
      return;
    }
  };

  const logOut = async () => {
    const url = `${config.backendUrl}/auth/logout`;
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
