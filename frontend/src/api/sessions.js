// Session API calls: upload CSV, list history, fetch one session.
import api from "./axios.js";

export const uploadSession = (formData) =>
  api.post("/sessions/upload", formData);
export const listSessions = () => api.get("/sessions");
export const getSession = (id) => api.get(`/sessions/${id}`);
