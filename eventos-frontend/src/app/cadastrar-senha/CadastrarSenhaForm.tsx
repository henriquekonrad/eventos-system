"use client";

import { useRouter, useSearchParams } from "next/navigation";
import { useState, useEffect, Suspense } from "react";

function FormContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const emailParam = searchParams.get("email") || "";

  const [email, setEmail] = useState(emailParam);
  const [nome, setNome] = useState("");
  const [cpf, setCpf] = useState("");
  const [senha, setSenha] = useState("");
  const [confirmarSenha, setConfirmarSenha] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [verificandoEmail, setVerificandoEmail] = useState(false);
  const [usuarioRapido, setUsuarioRapido] = useState<any>(null);

  useEffect(() => {
    if (emailParam) {
      verificarUsuarioRapido(emailParam);
    }
  }, [emailParam]);

  async function verificarUsuarioRapido(emailVerificar: string) {
    if (!emailVerificar || !emailVerificar.includes("@")) return;

    setVerificandoEmail(true);
    try {
      const response = await fetch(`/api/verificar-usuario-rapido?email=${encodeURIComponent(emailVerificar)}`);
      
      if (response.ok) {
        const data = await response.json();
        if (data.isRapido) {
          setUsuarioRapido(data.usuario);
          setNome(data.usuario.nome || "");
          setCpf(data.usuario.cpf || "");
        } else {
          setError("Este email não está cadastrado como usuário rápido.");
        }
      }
    } catch (err) {
      console.error("Erro ao verificar usuário:", err);
    } finally {
      setVerificandoEmail(false);
    }
  }

  function formatarCPF(valor: string) {
    const numeros = valor.replace(/\D/g, "");
    if (numeros.length <= 11) {
      return numeros
        .replace(/(\d{3})(\d)/, "$1.$2")
        .replace(/(\d{3})(\d)/, "$1.$2")
        .replace(/(\d{3})(\d{1,2})$/, "$1-$2");
    }
    return cpf;
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError("");

    if (!email.includes("@")) {
      setError("Email inválido");
      return;
    }

    if (!nome.trim()) {
      setError("O nome é obrigatório");
      return;
    }

    if (senha !== confirmarSenha) {
      setError("As senhas não coincidem");
      return;
    }

    if (senha.length < 6) {
      setError("A senha deve ter no mínimo 6 caracteres");
      return;
    }

    const cpfLimpo = cpf.replace(/\D/g, "");
    if (cpf && cpfLimpo.length !== 11) {
      setError("CPF inválido");
      return;
    }

    setLoading(true);

    try {
      const response = await fetch("/api/cadastrar-senha-rapido", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          email,
          nome: nome.trim(),
          cpf: cpfLimpo || undefined,
          senha 
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || "Erro ao cadastrar senha");
      }

      // Fazer login automático
      const loginResponse = await fetch("/api/session", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, senha }),
      });

      if (loginResponse.ok) {
        router.push("/app/eventos");
      } else {
        router.push("/login?message=Senha cadastrada com sucesso! Faça login.");
      }
    } catch (err: any) {
      console.error("Erro ao cadastrar senha:", err);
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
            Cadastrar Nova Senha
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Complete seu cadastro para acessar o sistema
          </p>
        </div>

        {usuarioRapido && (
          <div className="p-4 bg-blue-50 border border-blue-200 rounded-md">
            <p className="text-sm text-blue-800">
              <strong>Bem-vindo(a)!</strong> Você foi cadastrado rapidamente em um evento. 
              Complete seus dados abaixo para ter acesso completo ao sistema.
            </p>
          </div>
        )}

        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div className="rounded-md shadow-sm space-y-4">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                Email <span className="text-red-500">*</span>
              </label>
              <input
                id="email"
                name="email"
                type="email"
                required
                value={email}
                onChange={(e) => {
                  setEmail(e.target.value);
                  setUsuarioRapido(null);
                }}
                onBlur={(e) => verificarUsuarioRapido(e.target.value)}
                className="mt-1 appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                placeholder="seu@email.com"
                disabled={loading || verificandoEmail}
              />
              {verificandoEmail && (
                <p className="mt-1 text-xs text-gray-500">Verificando email...</p>
              )}
            </div>

            <div>
              <label htmlFor="nome" className="block text-sm font-medium text-gray-700">
                Nome completo <span className="text-red-500">*</span>
              </label>
              <input
                id="nome"
                name="nome"
                type="text"
                required
                value={nome}
                onChange={(e) => setNome(e.target.value)}
                className="mt-1 appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                placeholder="Seu nome completo"
                disabled={loading}
              />
            </div>

            <div>
              <label htmlFor="cpf" className="block text-sm font-medium text-gray-700">
                CPF (opcional)
              </label>
              <input
                id="cpf"
                name="cpf"
                type="text"
                value={cpf}
                onChange={(e) => setCpf(formatarCPF(e.target.value))}
                className="mt-1 appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                placeholder="000.000.000-00"
                disabled={loading}
                maxLength={14}
              />
            </div>

            <div className="pt-4 border-t border-gray-200">
              <p className="text-sm font-medium text-gray-700 mb-4">
                Defina sua senha de acesso
              </p>
              
              <div className="space-y-4">
                <div>
                  <label htmlFor="senha" className="block text-sm font-medium text-gray-700">
                    Nova senha <span className="text-red-500">*</span>
                  </label>
                  <input
                    id="senha"
                    name="senha"
                    type="password"
                    required
                    value={senha}
                    onChange={(e) => setSenha(e.target.value)}
                    className="mt-1 appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                    placeholder="Mínimo 6 caracteres"
                    disabled={loading}
                  />
                </div>

                <div>
                  <label htmlFor="confirmarSenha" className="block text-sm font-medium text-gray-700">
                    Confirmar senha <span className="text-red-500">*</span>
                  </label>
                  <input
                    id="confirmarSenha"
                    name="confirmarSenha"
                    type="password"
                    required
                    value={confirmarSenha}
                    onChange={(e) => setConfirmarSenha(e.target.value)}
                    className="mt-1 appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                    placeholder="Digite a senha novamente"
                    disabled={loading}
                  />
                </div>
              </div>
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
              disabled={loading || verificandoEmail || !usuarioRapido}
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? "Cadastrando..." : "Cadastrar Senha e Entrar"}
            </button>
          </div>

          <div className="text-center">
            <a
              href="/login"
              className="font-medium text-gray-600 hover:text-gray-500"
            >
              Voltar para o login
            </a>
          </div>
        </form>
      </div>
    </div>
  );
}

export default function CadastrarSenhaForm() {
  return (
    <Suspense fallback={<div className="min-h-screen flex items-center justify-center">Carregando...</div>}>
      <FormContent />
    </Suspense>
  );
}