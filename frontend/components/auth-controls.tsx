"use client";

import { useState, type FormEvent } from "react";
import { LogOut, ShieldCheck, X } from "lucide-react";

import { useAuth } from "@/components/auth-provider";
import { Button } from "@/components/ui/button";

function getErrorMessage(error: unknown, fallback: string) {
  return error instanceof Error ? error.message : fallback;
}

export function AuthControls() {
  const { user, authError, signIn, signUp, signOut } = useAuth();
  const [dialogOpen, setDialogOpen] = useState(false);
  const [mode, setMode] = useState<"sign-in" | "sign-up">("sign-in");
  const [displayName, setDisplayName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  const [messageType, setMessageType] = useState<"error" | "success">("error");

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setBusy(true);
    setMessage("");
    try {
      if (mode === "sign-up") {
        await signUp(displayName.trim(), email, password);
        setMessageType("success");
        setMessage("Your local account is ready.");
        setPassword("");
        setDialogOpen(false);
      } else {
        await signIn(email, password);
        setDialogOpen(false);
        setPassword("");
      }
    } catch (error) {
      setMessageType("error");
      setMessage(getErrorMessage(error, "Sign-in could not be completed."));
    } finally {
      setBusy(false);
    }
  }

  async function handleSignOut() {
    try {
      await signOut();
    } catch (error) {
      setMessage(getErrorMessage(error, "Sign-out could not be completed."));
    }
  }

  if (user) {
    return (
      <div className="flex items-center gap-3">
        <div className="hidden text-right sm:block">
          <p className="max-w-44 truncate text-xs font-semibold">{user.displayName || user.email}</p>
          <p className="text-[10px] text-muted">Local account</p>
        </div>
        <Button aria-label="Sign out" className="size-9" onClick={handleSignOut} size="icon" title="Sign out" variant="secondary">
          <LogOut aria-hidden="true" size={16} />
        </Button>
      </div>
    );
  }

  return (
    <>
      <Button onClick={() => setDialogOpen(true)} size="sm" variant="secondary">
        <ShieldCheck aria-hidden="true" size={15} />
        Sign in
      </Button>
      {dialogOpen && (
        <div className="fixed inset-0 z-50 grid place-items-center bg-slate-950/35 p-4" onMouseDown={(event) => {
          if (event.target === event.currentTarget) setDialogOpen(false);
        }}>
          <section aria-labelledby="signin-title" aria-modal="true" className="w-full max-w-sm rounded-lg border border-line bg-white p-6 shadow-2xl" role="dialog">
            <div className="mb-5 flex items-start justify-between">
              <div>
                <p className="text-[10px] font-semibold uppercase tracking-[0.14em] text-green">Secure access</p>
                <h2 className="mt-1 text-xl font-semibold" id="signin-title">{mode === "sign-up" ? "Create your account" : "Sign in to NyayaSetu"}</h2>
              </div>
              <Button aria-label="Close sign-in dialog" onClick={() => setDialogOpen(false)} size="icon" variant="ghost">
                <X aria-hidden="true" size={17} />
              </Button>
            </div>
            <form className="space-y-4" onSubmit={handleSubmit}>
                {authError && <p className="rounded-md border border-red-200 bg-red-50 p-3 text-xs leading-5 text-red-800" role="alert">Local session check failed: {authError}</p>}
                {mode === "sign-up" && <label className="block space-y-1.5 text-sm font-medium" htmlFor="signup-name">
                  Full name
                  <input autoComplete="name" className="h-10 w-full rounded-md border border-line px-3 text-sm outline-none transition focus:border-green focus:ring-2 focus:ring-green/15" id="signup-name" onChange={(event) => setDisplayName(event.target.value)} required value={displayName} />
                </label>}
                <label className="block space-y-1.5 text-sm font-medium" htmlFor="signin-email">
                  Email address
                  <input autoComplete="username" className="h-10 w-full rounded-md border border-line px-3 text-sm outline-none transition focus:border-green focus:ring-2 focus:ring-green/15" id="signin-email" onChange={(event) => setEmail(event.target.value)} required type="email" value={email} />
                </label>
                <label className="block space-y-1.5 text-sm font-medium" htmlFor="signin-password">
                  Password
                  <input autoComplete={mode === "sign-up" ? "new-password" : "current-password"} className="h-10 w-full rounded-md border border-line px-3 text-sm outline-none transition focus:border-green focus:ring-2 focus:ring-green/15" id="signin-password" minLength={mode === "sign-up" ? 8 : undefined} onChange={(event) => setPassword(event.target.value)} required type="password" value={password} />
                </label>
                {message && <p className={`text-sm leading-5 ${messageType === "success" ? "text-green-dark" : "text-red-700"}`} role={messageType === "success" ? "status" : "alert"}>{message}</p>}
                <Button className="w-full" disabled={busy} type="submit">{busy ? (mode === "sign-up" ? "Creating account..." : "Signing in...") : (mode === "sign-up" ? "Create account" : "Continue securely")}</Button>
                <p className="text-xs leading-5 text-muted">Accounts are stored locally. No email verification is required.</p>
                <p className="text-center text-xs text-muted">
                  {mode === "sign-up" ? "Already have an account?" : "New to NyayaSetu?"}{" "}
                  <button className="font-semibold text-green underline-offset-2 hover:underline" onClick={() => { setMode(mode === "sign-up" ? "sign-in" : "sign-up"); setMessage(""); setPassword(""); }} type="button">
                    {mode === "sign-up" ? "Sign in" : "Create account"}
                  </button>
                </p>
            </form>
          </section>
        </div>
      )}
    </>
  );
}
