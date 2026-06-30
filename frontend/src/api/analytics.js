// Analytics + LLM API calls.
import api from "./axios.js";

export const getSummary = () => api.get("/analytics/summary");
export const analyzeWorkout = (data) => api.post("/llm/analyze", data);
