"use client";

import { useRouter } from "next/navigation";
import { useState, useEffect } from "react";

export default function CompletarCadastroForm() {
  const router = useRouter();

  const [userData, setUserData] = useState<any>(null);
  const [nome, setNome] = useState("");
  const [cpf, setCpf] = useState("");
  const [senha, setSenha] = useState("");
  const [confirmarSenha, setConfirmarSenha] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const [loadingUser, setLoadingUser] = useState(true);

  useEffect(() => {
    async function buscarUsuario() {
      try {
        const response = await fetch("/api/me");
        if (!response.ok) {
          router.push("/login");
          return;
        }

        const data = await response.json();
        
        // Se não for usuário rápido, redirecionar
        if (data.papel !== "rapido") {
          router.push("eventos");
          return;
        }

        setUserData(data);
        setNome(data.nome || "");
        setCpf(data.cpf || "");
      } catch (err) {
        console.error("Erro ao buscar usuário:", err);
        router.push("/login");
      } finally {
        setLoadingUser(false);
      }
    }

    buscarUsuario();
  }, [router]);

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

    if (!nome.trim()) {
      setError("O nome é obrigatório");
      return;
    }

    if (senha && senha !== confirmarSenha) {
      setError("As senhas não coincidem");
      return;
    }

    if (senha && senha.length < 6) {
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
      const response = await fetch("/api/completar-cadastro", {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          nome: nome.trim(),
          cpf: cpfLimpo || undefined,
          senha: senha || undefined
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.message || "Erro ao completar cadastro");
      }

      // Redirecionar para página de eventos
      router.push("eventos");
    } catch (err: any) {
      console.error("Erro ao completar cadastro:", err);
      setError(err.message || "Erro ao conectar com o servidor");
    } finally {
      setLoading(false);
    }
  }

  if (loadingUser) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
          <p className="mt-4 text-gray-600">Carregando...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Complete seu cadastro
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Olá, <span className="font-semibold">{userData?.nome}</span>! 
            Para continuar usando o sistema, complete seus dados abaixo.
          </p>
          <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-md">
            <p className="text-sm text-blue-800">
              <strong>Email:</strong> {userData?.email}
            </p>
          </div>
        </div>

        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div className="rounded-md shadow-sm space-y-4">
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
              <p className="mt-1 text-xs text-gray-500">
                Atualize seu nome se necessário
              </p>
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
              <p className="text-sm font-medium text-gray-700 mb-2">
                Alterar senha (opcional)
              </p>
              <p className="text-xs text-gray-500 mb-4">
                Deixe em branco se não quiser alterar a senha
              </p>
              
              <div className="space-y-4">
                <div>
                  <label htmlFor="senha" className="block text-sm font-medium text-gray-700">
                    Nova senha
                  </label>
                  <input
                    id="senha"
                    name="senha"
                    type="password"
                    value={senha}
                    onChange={(e) => setSenha(e.target.value)}
                    className="mt-1 appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                    placeholder="Mínimo 6 caracteres"
                    disabled={loading}
                  />
                </div>

                {senha && (
                  <div>
                    <label htmlFor="confirmarSenha" className="block text-sm font-medium text-gray-700">
                      Confirmar nova senha
                    </label>
                    <input
                      id="confirmarSenha"
                      name="confirmarSenha"
                      type="password"
                      value={confirmarSenha}
                      onChange={(e) => setConfirmarSenha(e.target.value)}
                      className="mt-1 appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm"
                      placeholder="Digite a senha novamente"
                      disabled={loading}
                    />
                  </div>
                )}
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
              disabled={loading}
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? "Salvando..." : "Completar cadastro"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}