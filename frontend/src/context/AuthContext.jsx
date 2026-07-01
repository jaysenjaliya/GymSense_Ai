// Auth state: current user, login/register/logout, token persistence + bootstrap.
import { createContext, useEffect, useState } from "react";

import * as authApi from "../api/auth.js";
import { tokenStore } from "../api/axios.js";

export const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Bootstrap: if we have a token, resolve the current user.
  useEffect(() => {
    (async () => {
      if (tokenStore.access) {
        try {
          const { data } = await authApi.getMe();
          setUser(data);
        } catch {
          tokenStore.clear();
        }
      }
      setLoading(false);
    })();
  }, []);

  const login = async (email, password) => {
    const { data } = await authApi.login({ email, password });
    tokenStore.save(data);
    const me = await authApi.getMe();
    setUser(me.data);
    return me.data;
  };

  const register = async (payload) => {
    await authApi.register(payload);
    return login(payload.email, payload.password);
  };

  const logout = () => {
    tokenStore.clear();
    setUser(null);
  };

  const value = { user, loading, login, register, logout };
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
