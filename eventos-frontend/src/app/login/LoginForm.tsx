"use client";

import { useSearchParams, useRouter } from "next/navigation";
import { useState, Suspense } from "react";

function FormContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const redirect = searchParams.get("redirect") || "eventos";

  const [email, setEmail] = useState("");
  const [senha, setSenha] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const response = await fetch("/api/session", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, senha }),
      });

      const contentType = response.headers.get("content-type");
      if (!contentType || !contentType.includes("application/json")) {
        throw new Error("Resposta inválida do servidor");
      }

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || "Erro ao fazer login");
      }

      if (data.requiresCompletion) {
        router.push("completar-cadastro");
      } else {
        router.push(redirect);
      }
    } catch (err: any) {
      console.error("Erro no login:", err);
      setError(err.message || "Erro ao conectar com o servidor");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Sistema de Eventos
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Faça login para acessar sua conta
          </p>
        </div>

        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div className="rounded-md shadow-sm -space-y-px">
            <div>
              <label htmlFor="email" className="sr-only">
                Email
              </label>
              <input
                id="email"
                name="email"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-t-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                placeholder="Email"
                disabled={loading}
              />
            </div>
            <div>
              <label htmlFor="senha" className="sr-only">
                Senha
              </label>
              <input
                id="senha"
                name="senha"
                type="password"
                required
                value={senha}
                onChange={(e) => setSenha(e.target.value)}
                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-b-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
                placeholder="Senha"
                disabled={loading}
              />
            </div>
          </div>

          {error && (
            <div className="rounded-md bg-red-50 p-4">
              <div className="flex">
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-red-800">{error}</h3>
                </div>
              </div>
            </div>
          )}

          <div>
            <button
              type="submit"
              disabled={loading}
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? "Entrando..." : "Entrar"}
            </button>
          </div>

          <div className="text-center space-y-2">
            <div>
              <a
                href="/registrar"
                className="font-medium text-indigo-600 hover:text-indigo-500"
              >
                Não tem conta? Cadastre-se
              </a>
            </div>
            <div>
              <a
                href="/eventos-publicos"
                className="font-medium text-gray-600 hover:text-gray-500"
              >
                Ver eventos públicos
              </a>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}

export default function LoginForm() {
  return (
    <Suspense fallback={<div>Carregando login...</div>}>
      <FormContent />
    </Suspense>
  );
}
