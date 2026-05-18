import { createContext, useCallback, useEffect, useState, type ReactNode } from "react";
import { api, tokenStorage } from "../lib/api";
import type { CurrentUser, TokenResponse } from "../types";

interface AuthState {
  user: CurrentUser | null;
  loading: boolean;
  login: (username: string, password: string) => Promise<TokenResponse>;
  logout: () => void;
  refreshUser: () => Promise<void>;
  setPrimerLoginFalse: () => void;
}

// eslint-disable-next-line react-refresh/only-export-components
export const AuthContext = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<CurrentUser | null>(null);
  const [loading, setLoading] = useState(true);

  const refreshUser = useCallback(async () => {
    if (!tokenStorage.get()) {
      setUser(null);
      setLoading(false);
      return;
    }
    try {
      const { data } = await api.get<CurrentUser>("/auth/me");
      setUser(data);
    } catch {
      tokenStorage.clear();
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refreshUser();
  }, [refreshUser]);

  const login = useCallback(async (username: string, password: string) => {
    const body = new URLSearchParams({ username, password });
    const { data } = await api.post<TokenResponse>("/auth/token", body, {
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
    });
    tokenStorage.set(data.access_token);
    await refreshUser();
    return data;
  }, [refreshUser]);

  const logout = useCallback(() => {
    tokenStorage.clear();
    setUser(null);
  }, []);

  const setPrimerLoginFalse = useCallback(() => {
    setUser((u) => (u ? { ...u, primer_login: false } : u));
  }, []);

  return (
    <AuthContext.Provider value={{ user, loading, login, logout, refreshUser, setPrimerLoginFalse }}>
      {children}
    </AuthContext.Provider>
  );
}
