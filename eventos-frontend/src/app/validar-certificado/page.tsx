"use client";

export const dynamic = "force-dynamic";

import { useState, useEffect } from "react";
import { useSearchParams } from "next/navigation";

export default function ValidarCertificadoPage() {
  const searchParams = useSearchParams();
  const codigoUrl = searchParams.get("codigo");

  const [codigo, setCodigo] = useState(codigoUrl || "");
  const [resultado, setResultado] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (codigoUrl) {
      validar(codigoUrl);
    }
  }, [codigoUrl]);

  async function validar(codigoParaValidar?: string) {
    const codigoFinal = codigoParaValidar || codigo;

    if (!codigoFinal) {
      setError("Por favor, insira um código");
      return;
    }

    setError("");
    setLoading(true);
    setResultado(null);

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_CERTIFICADOS_URL}/codigo/${codigoFinal}`,
        {
          headers: {
            "x-api-key": process.env.NEXT_PUBLIC_API_KEY || "",
          },
        }
      );

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || "Certificado não encontrado");
      }

      const data = await response.json();
      setResultado(data);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    validar();
  }

  function formatarData(data: string) {
    return new Date(data).toLocaleString("pt-BR", {
      day: "2-digit",
      month: "2-digit",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-3xl mx-auto">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">
            Validar Certificado
          </h1>
          <p className="mt-2 text-sm text-gray-600">
            Insira o código de autenticação para verificar a validade do
            certificado
          </p>
        </div>

        <div className="bg-white shadow rounded-lg p-6 mb-6">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label
                htmlFor="codigo"
                className="block text-sm font-medium text-gray-700"
              >
                Código de Autenticação
              </label>
              <input
                id="codigo"
                type="text"
                value={codigo}
                onChange={(e) => setCodigo(e.target.value)}
                placeholder="Ex: abc123xyz456"
                className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
            >
              {loading ? "Validando..." : "Validar Certificado"}
            </button>
          </form>
        </div>

        {error && (
          <div className="bg-red-50 border-l-4 border-red-400 p-4 rounded">
            <div className="flex">
              <div className="flex-shrink-0">
                <svg
                  className="h-5 w-5 text-red-400"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path
                    fillRule="evenodd"
                    d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                    clipRule="evenodd"
                  />
                </svg>
              </div>
              <div className="ml-3">
                <h3 className="text-sm font-medium text-red-800">{error}</h3>
              </div>
            </div>
          </div>
        )}

        {resultado && (
          <div
            className={`border-l-4 p-6 rounded ${
              resultado.revogado
                ? "bg-red-50 border-red-400"
                : "bg-green-50 border-green-400"
            }`}
          >
            {resultado.revogado ? (
              <>
                <div className="flex items-center mb-4">
                  <svg
                    className="h-6 w-6 text-red-600 mr-2"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path
                      fillRule="evenodd"
                      d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                      clipRule="evenodd"
                    />
                  </svg>
                  <h3 className="text-lg font-bold text-red-900">
                    Certificado Revogado
                  </h3>
                </div>
                <p className="text-sm text-red-700">
                  Este certificado foi revogado e não é mais válido.
                </p>
              </>
            ) : (
              <>
                <div className="flex items-center mb-4">
                  <svg
                    className="h-6 w-6 text-green-600 mr-2"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path
                      fillRule="evenodd"
                      d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                      clipRule="evenodd"
                    />
                  </svg>
                  <h3 className="text-lg font-bold text-green-900">
                    Certificado Válido
                  </h3>
                </div>

                <div className="space-y-3 text-sm">
                  <div>
                    <span className="font-semibold text-gray-700">Código:</span>
                    <span className="ml-2 font-mono text-gray-900">
                      {resultado.codigo_certificado}
                    </span>
                  </div>

                  <div>
                    <span className="font-semibold text-gray-700">
                      Emitido em:
                    </span>
                    <span className="ml-2 text-gray-900">
                      {formatarData(resultado.emitido_em)}
                    </span>
                  </div>

                  <div>
                    <span className="font-semibold text-gray-700">
                      ID do Certificado:
                    </span>
                    <span className="ml-2 text-gray-900">{resultado.id}</span>
                  </div>
                </div>
              </>
            )}
          </div>
        )}

        <div className="mt-8 text-center">
          <a
            href="/"
            className="text-indigo-600 hover:text-indigo-800 font-medium"
          >
            ← Voltar para home
          </a>
        </div>
      </div>
    </div>
  );
}