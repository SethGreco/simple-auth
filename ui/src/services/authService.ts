import { redirect } from "react-router-dom";
import { LoginResponse } from "./models";
import { config } from "../config/config";

export const login = async (username: string, password: string) => {
  const url = `${config.backendUrl}/login/user/`;
  const response = await fetch(url, {
    method: "POST",
    headers: {
      Authorization: `Basic ${btoa(`${username}:${password}`)}`,
      "Content-Type": "application/json",
    },
  });
  const data: LoginResponse = await response.json();

  if (response.ok) {
    localStorage.setItem("token", data.accessToken as string);
    return {
      status: 200,
      message: "Success",
    };
  }
  return {
    status: response.status,
    message: data.detail,
  };
};

export const logout = async (): Promise<void> => {
  const token = localStorage.getItem("token");
  if (token) {
    localStorage.removeItem("token");
  }
};

export const getAuthToken = (): string | null => {
  const token = localStorage.getItem("token");
  return token;
};

export const isAuthenticated = (): string | Response => {
  const token = getAuthToken();
  if (!token) {
    return redirect("/login");
  }
  // TODO: Need to validate token has not expired
  return token;
};
