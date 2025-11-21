import axios from "axios";

const CERTIFICADOS_URL = process.env.NEXT_PUBLIC_CERTIFICADOS_URL;
const CERTIFICADOS_API_KEY = process.env.NEXT_PUBLIC_CERTIFICADOS_API_KEY;

async function fetchCertificado(codigo: string) {
  try {
    const r = await axios.get(`${CERTIFICADOS_URL}/codigo/${codigo}`, {
      headers: { "x-api-key": CERTIFICADOS_API_KEY }
    });
    return r.data;
  } catch (err: any) {
    console.error("Erro ao buscar certificado:", err.response?.data || err.message);
    return null;
  }
}

function formatarData(dataString: string) {
  try {
    return new Date(dataString).toLocaleDateString("pt-BR", {
      day: "2-digit",
      month: "long",
      year: "numeric",
    });
  } catch {
    return "Data não disponível";
  }
}

export default async function ValidarCertificadoPage({
  params,
}: {
  params: { codigo: string };
}) {
  const { codigo } = await params;
  const certificado = await fetchCertificado(codigo);

  if (!certificado) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="max-w-md w-full bg-white rounded-xl shadow-lg p-8 text-center">
          <div className="w-16 h-16 mx-auto bg-red-100 rounded-full flex items-center justify-center">
            <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </div>
          <h1 className="mt-4 text-xl font-bold text-gray-900">Certificado Não Encontrado</h1>
          <p className="mt-2 text-gray-600">
            O código <span className="font-mono bg-gray-100 px-2 py-1 rounded">{codigo}</span> não corresponde a nenhum certificado válido.
          </p>
          <a href="/" className="mt-6 inline-block text-indigo-600 hover:text-indigo-500">
            Voltar ao início
          </a>
        </div>
      </div>
    );
  }

  const isRevogado = certificado.revogado;

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4">
      <div className="max-w-2xl mx-auto">
        {/* Header de validação */}
        <div className={`rounded-xl shadow-lg p-8 ${isRevogado ? 'bg-red-50 border-2 border-red-200' : 'bg-green-50 border-2 border-green-200'}`}>
          <div className="flex items-center justify-center gap-4">
            {isRevogado ? (
              <>
                <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center">
                  <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </div>
                <div>
                  <h1 className="text-2xl font-bold text-red-800">Certificado Revogado</h1>
                  <p className="text-red-600">Este certificado foi invalidado</p>
                </div>
              </>
            ) : (
              <>
                <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center">
                  <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <div>
                  <h1 className="text-2xl font-bold text-green-800">Certificado Válido</h1>
                  <p className="text-green-600">Autenticidade verificada com sucesso</p>
                </div>
              </>
            )}
          </div>
        </div>

        {/* Detalhes do certificado */}
        <div className="mt-6 bg-white rounded-xl shadow-lg p-8">
          <h2 className="text-lg font-semibold text-gray-900 mb-6 pb-4 border-b">
            Detalhes do Certificado
          </h2>

          <div className="space-y-4">
            <div>
              <p className="text-sm text-gray-500">Participante</p>
              <p className="text-lg font-medium text-gray-900">
                {certificado.participante?.nome || "Não informado"}
              </p>
            </div>

            <div>
              <p className="text-sm text-gray-500">Evento</p>
              <p className="text-lg font-medium text-gray-900">
                {certificado.evento?.titulo || "Evento não encontrado"}
              </p>
            </div>

            {certificado.evento?.inicio_em && (
              <div>
                <p className="text-sm text-gray-500">Data do Evento</p>
                <p className="text-lg font-medium text-gray-900">
                  {formatarData(certificado.evento.inicio_em)}
                </p>
              </div>
            )}

            {certificado.evento?.local && (
              <div>
                <p className="text-sm text-gray-500">Local</p>
                <p className="text-lg font-medium text-gray-900">
                  {certificado.evento.local}
                </p>
              </div>
            )}

            <div>
              <p className="text-sm text-gray-500">Data de Emissão</p>
              <p className="text-lg font-medium text-gray-900">
                {formatarData(certificado.emitido_em)}
              </p>
            </div>

            <div className="pt-4 border-t">
              <p className="text-sm text-gray-500">Código de Autenticação</p>
              <p className="text-lg font-mono font-medium text-gray-900 bg-gray-50 px-3 py-2 rounded mt-1">
                {certificado.codigo_certificado}
              </p>
            </div>
          </div>
        </div>

        {/* Rodapé */}
        <div className="mt-6 text-center text-sm text-gray-500">
          <p>Sistema de Eventos - Validação de Certificados</p>
          <p className="mt-1">
            Este certificado foi verificado em {new Date().toLocaleDateString("pt-BR")}
          </p>
        </div>
      </div>
    </div>
  );
}