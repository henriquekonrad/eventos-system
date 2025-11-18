import { getCurrentUser, fetchMeusCertificados } from "@/lib/api";
import { redirect } from "next/navigation";
import CertificadoCard from "../components/CertificadoCard";

export const dynamic = "force-dynamic";

export default async function CertificadosPage() {
  const user = await getCurrentUser();

  if (!user) {
    redirect("/login");
  }

  const certificados = await fetchMeusCertificados();

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <a
                href="/app/eventos"
                className="text-xl font-semibold hover:text-indigo-600"
              >
                Sistema de Eventos
              </a>
            </div>
            <div className="flex items-center space-x-4">
              <a href="/app/eventos" className="text-gray-700 hover:text-gray-900">
                Eventos
              </a>
              <a
                href="/app/minhas-inscricoes"
                className="text-gray-700 hover:text-gray-900"
              >
                Minhas Inscrições
              </a>
              <div className="border-l border-gray-300 h-6"></div>
              <span className="text-sm text-gray-600">{user.nome}</span>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="mb-6">
            <h2 className="text-2xl font-bold text-gray-900">
              Meus Certificados
            </h2>
            <p className="mt-2 text-sm text-gray-600">
              Certificados são emitidos automaticamente após confirmação de presença
              (check-in) no evento.
            </p>
          </div>

          {certificados.length === 0 ? (
            <div className="text-center py-12 bg-white rounded-lg shadow">
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
                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                />
              </svg>
              <h3 className="mt-2 text-sm font-medium text-gray-900">
                Nenhum certificado disponível
              </h3>
              <p className="mt-1 text-sm text-gray-500">
                Você receberá certificados após participar de eventos.
              </p>
              <div className="mt-6">
                <a
                  href="/app/eventos"
                  className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700"
                >
                  Ver Eventos
                </a>
              </div>
            </div>
          ) : (
            <>
              <div className="bg-blue-50 border-l-4 border-blue-400 p-4 mb-6">
                <div className="flex">
                  <div className="flex-shrink-0">
                    <svg
                      className="h-5 w-5 text-blue-400"
                      fill="currentColor"
                      viewBox="0 0 20 20"
                    >
                      <path
                        fillRule="evenodd"
                        d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
                        clipRule="evenodd"
                      />
                    </svg>
                  </div>
                  <div className="ml-3">
                    <p className="text-sm text-blue-700">
                      Cada certificado possui um código único de autenticação. Use
                      esse código para validar a autenticidade do documento.
                    </p>
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
                {certificados.map((certificado: any) => (
                  <CertificadoCard
                    key={certificado.id}
                    certificado={certificado}
                  />
                ))}
              </div>
            </>
          )}
        </div>
      </main>
    </div>
  );
}