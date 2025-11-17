"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");
  const [err, setErr] = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setErr("");
    try {
      const r = await fetch("/api/session", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, senha }),
      });

      if (!r.ok) throw new Error("Erro ao logar");

      router.push("/app/eventos");
    } catch (e: any) {
      setErr(e.message);
    }
  }

  return (
    <main style={{ maxWidth: 600, margin: "4rem auto" }}>
      <h1>Login</h1>
      <form onSubmit={handleSubmit}>
        <input value={email} onChange={(e) => setEmail(e.target.value)} placeholder="email" />
        <input value={senha} onChange={(e) => setSenha(e.target.value)} placeholder="senha" type="password" />
        <button type="submit">Entrar</button>
      </form>
      {err && <p style={{ color: "red" }}>{err}</p>}
    </main>
  );
}
