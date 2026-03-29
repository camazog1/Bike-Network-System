import { useState, useCallback } from 'react';
import type { ReactNode } from 'react';
import { AuthContext } from './AuthContextDef';
import type { AuthUser, AuthSession } from './authTypes';

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [idToken, setIdToken] = useState<string | null>(
    () => localStorage.getItem('bns_id_token'),
  );

  const login = useCallback((session: AuthSession) => {
    localStorage.setItem('bns_id_token', session.idToken);
    localStorage.setItem('bns_refresh_token', session.refreshToken);
    setUser(session.user);
    setIdToken(session.idToken);
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem('bns_id_token');
    localStorage.removeItem('bns_refresh_token');
    setUser(null);
    setIdToken(null);
  }, []);

  return (
    <AuthContext.Provider value={{ user, idToken, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}
