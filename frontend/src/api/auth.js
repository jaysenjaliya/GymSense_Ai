// Auth API calls: register, login, refresh, current user.
import api from "./axios.js";

export const register = (data) => api.post("/auth/register", data);
export const login = (data) => api.post("/auth/login", data);
export const refresh = (refresh_token) =>
  api.post("/auth/refresh", { refresh_token });
export const getMe = () => api.get("/auth/me");
