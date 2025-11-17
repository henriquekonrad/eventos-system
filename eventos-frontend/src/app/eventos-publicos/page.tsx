import { fetchEventosPublicos } from "@/lib/api";
import Link from "next/link";

export const dynamic = "force-dynamic";

export default async function EventosPublicosPage() {
  const eventos = await fetchEventosPublicos();

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
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <Link href="/" className="text-xl font-bold text-indigo-600">
                Sistema de Eventos
              </Link>
            </div>
            <div className="flex items-center space-x-4">
              <Link
                href="/validar-certificado"
                className="text-gray-700 hover:text-gray-900"
              >
                Validar Certificado
              </Link>
              <Link
                href="/login"
                className="bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700"
              >
                Entrar
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="mb-6">
            <h1 className="text-3xl font-bold text-gray-900">
              Eventos Disponíveis
            </h1>
            <p className="mt-2 text-sm text-gray-600">
              Faça login para se inscrever nos eventos
            </p>
          </div>

          {eventos.length === 0 ? (
            <div className="bg-white shadow rounded-lg p-12 text-center">
              <svg
                className="mx-auto h-12 w-12 text-gray-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                />
              </svg>
              <h3 className="mt-2 text-sm font-medium text-gray-900">
                Nenhum evento disponível
              </h3>
              <p className="mt-1 text-sm text-gray-500">
                Volte mais tarde para conferir novos eventos.
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
              {eventos.map((evento: any) => (
                <div
                  key={evento.id}
                  className="bg-white overflow-hidden shadow-lg rounded-lg hover:shadow-xl transition-shadow"
                >
                  <div className="p-6">
                    <h3 className="text-xl font-bold text-gray-900 mb-3">
                      {evento.titulo}
                    </h3>

                    <p className="text-sm text-gray-600 mb-4 line-clamp-3">
                      {evento.descricao}
                    </p>

                    <div className="space-y-2 text-sm text-gray-500 mb-4">
                      <div className="flex items-center">
                        <svg
                          className="h-5 w-5 mr-2 text-indigo-500"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                          />
                        </svg>
                        <div>
                          <p className="font-medium text-gray-700">Início</p>
                          <p>{formatarData(evento.inicio_em)}</p>
                        </div>
                      </div>

                      <div className="flex items-center">
                        <svg
                          className="h-5 w-5 mr-2 text-indigo-500"
                          fill="none"
                          stroke="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"
                          />
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"
                          />
                        </svg>
                        <div>
                          <p className="font-medium text-gray-700">Local</p>
                          <p>{evento.local}</p>
                        </div>
                      </div>
                    </div>

                    <Link
                      href="/login"
                      className="block w-full text-center bg-indigo-600 text-white px-4 py-2 rounded-md hover:bg-indigo-700 font-medium"
                    >
                      Fazer Login para Inscrever
                    </Link>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </main>
    </div>
  );
}