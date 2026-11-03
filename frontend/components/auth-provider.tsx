"use client";

import {
  createContext,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";

import { createAccount, getCurrentUser, signIn as signInRequest, signOut as signOutRequest } from "@/lib/api";
import type { SessionUser } from "@/lib/types";

interface AuthContextValue {
  user: SessionUser | null;
  authReady: boolean;
  authError: string | null;
  signIn: (email: string, password: string) => Promise<void>;
  signUp: (displayName: string, email: string, password: string) => Promise<void>;
  signOut: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<SessionUser | null>(null);
  const [authReady, setAuthReady] = useState(false);
  const [authError, setAuthError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    void getCurrentUser()
      .then((currentUser) => {
        if (cancelled) return;
        setUser(currentUser);
        setAuthError(null);
      })
      .catch((error: unknown) => {
        if (!cancelled) setAuthError(error instanceof Error ? error.message : "The local session could not be checked.");
      })
      .finally(() => {
        if (!cancelled) setAuthReady(true);
      });
    return () => { cancelled = true; };
  }, []);

  async function signIn(email: string, password: string) {
    setUser(await signInRequest(email, password));
  }

  async function signUp(displayName: string, email: string, password: string) {
    setUser(await createAccount(displayName, email, password));
  }

  async function signOut() {
    await signOutRequest();
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ user, authReady, authError, signIn, signUp, signOut }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error("useAuth must be used within AuthProvider.");
  return context;
}
