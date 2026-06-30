// Configured Axios instance: base URL + JWT attach/refresh interceptors.
import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
});

// TODO: request interceptor — attach access token from storage.
// TODO: response interceptor — on 401, try refresh token, then retry once.

export default api;
