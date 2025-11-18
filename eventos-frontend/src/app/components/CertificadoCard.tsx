"use client";

export default function CertificadoCard({ certificado }: any) {
  const data = new Date(certificado.data_emissao).toLocaleDateString("pt-BR", {
    day: "2-digit",
    month: "long",
    year: "numeric",
  });

  const baixarUrl = certificado.url_pdf;
  const validarUrl = `/validar-certificado/${certificado.codigo_autenticacao}`;

  return (
    <div className="bg-white rounded-xl shadow-md border border-gray-200 p-6 hover:shadow-lg transition-shadow flex flex-col justify-between">
      <div>
        <h3 className="text-lg font-semibold text-gray-900">
          {certificado.evento_titulo}
        </h3>

        <p className="mt-1 text-sm text-gray-600">
          Emitido em <span className="font-medium">{data}</span>
        </p>

        <div className="mt-4 bg-gray-50 p-3 rounded-lg border border-gray-200">
          <p className="text-xs text-gray-500">Código de Autenticação:</p>
          <p className="text-sm font-mono font-medium text-gray-900">
            {certificado.codigo_autenticacao}
          </p>
        </div>
      </div>

      <div className="mt-6 flex flex-col gap-3">
        <a
          href={baixarUrl}
          target="_blank"
          className="w-full text-center px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white font-medium"
        >
          Baixar PDF
        </a>

        <a
          href={validarUrl}
          target="_blank"
          className="w-full text-center px-4 py-2 rounded-lg bg-gray-100 hover:bg-gray-200 text-gray-800 font-medium"
        >
          Validar Autenticidade
        </a>
      </div>
    </div>
  );
}
