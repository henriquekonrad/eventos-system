"use client";

import { useRef } from "react";

function formatarData(dataString: string) {
  try {
    return new Date(dataString).toLocaleDateString("pt-BR", {
      day: "2-digit",
      month: "long",
      year: "numeric",
    });
  } catch {
    return "";
  }
}

export default function CertificadoView({ certificado }: { certificado: any }) {
  const certificadoRef = useRef<HTMLDivElement>(null);

  function handlePrint() {
    window.print();
  }

  return (
    <div className="min-h-screen bg-gray-100 py-8 px-4">
      {/* Botões de ação - não aparecem na impressão */}
      <div className="max-w-4xl mx-auto mb-6 flex gap-4 print:hidden">
        <button
          onClick={handlePrint}
          className="px-6 py-2 bg-indigo-600 hover:bg-indigo-700 text-white font-medium rounded-lg flex items-center gap-2"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
          </svg>
          Imprimir / Salvar PDF
        </button>
        <a
          href={`/validar-certificado/${certificado.codigo_certificado}`}
          className="px-6 py-2 bg-gray-200 hover:bg-gray-300 text-gray-700 font-medium rounded-lg"
        >
          Validar Autenticidade
        </a>
        <a href="/minhas-inscricoes" className="px-6 py-2 text-gray-600 hover:text-gray-800">
          ← Voltar
        </a>
      </div>

      {/* Certificado - formatado para impressão */}
      <div
        ref={certificadoRef}
        className="max-w-4xl mx-auto bg-white shadow-2xl print:shadow-none"
      >
        {/* Borda decorativa */}
        <div className="border-8 border-double border-indigo-200 p-8 md:p-12">
          {/* Header */}
          <div className="text-center border-b-2 border-indigo-100 pb-8">
            <h1 className="text-4xl md:text-5xl font-serif font-bold text-indigo-900 tracking-wide">
              CERTIFICADO
            </h1>
            <p className="mt-2 text-lg text-gray-500 uppercase tracking-widest">
              de Participação
            </p>
          </div>

          {/* Conteúdo */}
          <div className="py-12 text-center">
            <p className="text-lg text-gray-600">Certificamos que</p>
            
            <h2 className="mt-4 text-3xl md:text-4xl font-serif font-bold text-gray-900">
              {certificado.participante?.nome || "Participante"}
            </h2>

            <p className="mt-8 text-lg text-gray-600 max-w-2xl mx-auto">
              participou do evento
            </p>

            <h3 className="mt-4 text-2xl md:text-3xl font-semibold text-indigo-800">
              {certificado.evento?.titulo || "Evento"}
            </h3>

            {certificado.evento?.inicio_em && (
              <p className="mt-4 text-lg text-gray-600">
                realizado em{" "}
                <span className="font-medium">
                  {formatarData(certificado.evento.inicio_em)}
                </span>
              </p>
            )}

            {certificado.evento?.local && (
              <p className="mt-2 text-gray-500">
                Local: {certificado.evento.local}
              </p>
            )}
          </div>

          {/* Rodapé com código de validação */}
          <div className="border-t-2 border-indigo-100 pt-8 mt-8">
            <div className="flex flex-col md:flex-row justify-between items-center gap-6">
              <div className="text-center md:text-left">
                <p className="text-sm text-gray-500">Data de Emissão</p>
                <p className="font-medium text-gray-700">
                  {formatarData(certificado.emitido_em)}
                </p>
              </div>

              <div className="text-center">
                <div className="border-t-2 border-gray-400 pt-2 px-12">
                  <p className="text-sm text-gray-600">Sistema de Eventos</p>
                </div>
              </div>

              <div className="text-center md:text-right">
                <p className="text-sm text-gray-500">Código de Validação</p>
                <p className="font-mono font-medium text-gray-700">
                  {certificado.codigo_certificado}
                </p>
              </div>
            </div>

            <p className="mt-6 text-center text-xs text-gray-400">
              Valide este certificado em: {typeof window !== "undefined" ? window.location.origin : ""}/validar-certificado/{certificado.codigo_certificado}
            </p>
          </div>
        </div>
      </div>

      {/* Estilo de impressão */}
      <style jsx global>{`
        @media print {
          body {
            background: white !important;
            -webkit-print-color-adjust: exact;
            print-color-adjust: exact;
          }
          .print\\:hidden {
            display: none !important;
          }
          .print\\:shadow-none {
            box-shadow: none !important;
          }
        }
      `}</style>
    </div>
  );
}