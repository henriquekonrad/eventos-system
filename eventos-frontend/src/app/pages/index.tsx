// pages/index.tsx
import { useState } from "react";
import { useRouter } from "next/router";

export default function Login(){
  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");
  const [err, setErr] = useState("");
  const router = useRouter();

  async function handleSubmit(e: React.FormEvent){
    e.preventDefault();
    setErr("");
    try {
      const r = await fetch("/api/session", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, senha })
      });
      if (!r.ok) {
        const j = await r.json();
        throw new Error(j.detail || j.message || "Erro");
      }
      // login ok -> redireciona para dashboard
      router.push("/app/eventos");
    } catch (e: any) {
      setErr(e.message);
    }
  }

  return (
    <main style={{maxWidth:600, margin:"4rem auto"}}>
      <h1>Login</h1>
      <form onSubmit={handleSubmit}>
        <input value={email} onChange={e=>setEmail(e.target.value)} placeholder="email" />
        <input value={senha} onChange={e=>setSenha(e.target.value)} placeholder="senha" type="password" />
        <button type="submit">Entrar</button>
      </form>
      {err && <p style={{color:"red"}}>{err}</p>}
    </main>
  );
}
