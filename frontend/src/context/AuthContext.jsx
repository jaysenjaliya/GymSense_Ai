// Auth state: current user, tokens, login/logout. Persists tokens to storage.
import { createContext, useState } from "react";

export const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);

  // TODO: login(), logout(), token persistence + bootstrap from storage.
  const value = { user, setUser };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
