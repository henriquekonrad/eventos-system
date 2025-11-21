"use client";

import { useState } from "react";
import axios from "axios";

export default function InscricoesList({ inscricoes }: { inscricoes: any[] }) {
  const [loadingId, setLoadingId] = useState<string | null>(null);
  const [inscricoesState, setInscricoesState] = useState(inscricoes);

  function formatarData(dataString: string) {
    try {
      const data = new Date(dataString);
      if (isNaN(data.getTime())) return "Data não disponível";
      return data.toLocaleDateString("pt-BR", {
        day: "2-digit",
        month: "long",
        year: "numeric",
      });
    } catch {
      return "Data inválida";
    }
  }

  function isEventoFuturo(dataInicio: string) {
    return new Date(dataInicio) > new Date();
  }

  async function cancelarInscricao(inscricaoId: string) {
    if (!confirm("Tem certeza que deseja cancelar esta inscrição?")) return;

    setLoadingId(inscricaoId);
    try {
      const r = await axios.post("/api/cancelar-inscricao", { inscricao_id: inscricaoId });
      
      if (r.data.ok) {
        setInscricoesState(prev =>
          prev.map(i => i.id === inscricaoId ? { ...i, status: "cancelada" } : i)
        );
        alert("Inscrição cancelada com sucesso!");
      }
    } catch (err: any) {
      const msg = err.response?.data?.message || "Erro ao cancelar inscrição";
      alert(`Erro: ${msg}`);
    } finally {
      setLoadingId(null);
    }
  }

  function getStatusBadge(inscricao: any) {
    if (inscricao.status === "cancelada") {
      return <span className="px-2 py-1 text-xs font-medium rounded-full bg-red-100 text-red-700">Cancelada</span>;
    }
    if (inscricao.tem_checkin) {
      return <span className="px-2 py-1 text-xs font-medium rounded-full bg-green-100 text-green-700">✓ Presença confirmada</span>;
    }
    if (isEventoFuturo(inscricao.evento?.inicio_em)) {
      return <span className="px-2 py-1 text-xs font-medium rounded-full bg-blue-100 text-blue-700">Confirmada</span>;
    }
    return <span className="px-2 py-1 text-xs font-medium rounded-full bg-yellow-100 text-yellow-700">Não compareceu</span>;
  }

  return (
    <div className="space-y-4">
      {inscricoesState.map((inscricao) => {
        const evento = inscricao.evento;
        const futuro = evento && isEventoFuturo(evento.inicio_em);
        const podeCancelar = futuro && inscricao.status === "ativa" && !inscricao.tem_checkin;
        const temCertificado = inscricao.certificado && !inscricao.certificado.revogado;

        return (
          <div
            key={inscricao.id}
            className={`bg-white rounded-xl shadow-md border p-6 ${
              inscricao.status === "cancelada" ? "border-red-200 bg-red-50/30" : "border-gray-200"
            }`}
          >
            <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4">
              <div className="flex-1">
                <div className="flex items-center gap-3 flex-wrap">
                  <h3 className="text-lg font-semibold text-gray-900">
                    {evento?.titulo || "Evento não encontrado"}
                  </h3>
                  {getStatusBadge(inscricao)}
                </div>

                {evento && (
                  <div className="mt-2 text-sm text-gray-600 space-y-1">
                    <p><span className="font-medium">Data:</span> {formatarData(evento.inicio_em)}</p>
                    {evento.local && <p><span className="font-medium">Local:</span> {evento.local}</p>}
                  </div>
                )}

                {inscricao.tem_checkin && (
                  <p className="mt-2 text-sm text-green-600">
                    ✓ Check-in realizado
                  </p>
                )}
              </div>

              <div className="flex flex-col gap-2 min-w-[180px]">
                {temCertificado && (
                  <>
                    <a
                      href={`/certificado/${inscricao.certificado.codigo_certificado}`}
                      className="w-full text-center px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-700 text-white font-medium text-sm"
                    >
                      Ver Certificado
                    </a>
                    <a
                      href={`/validar-certificado/${inscricao.certificado.codigo_certificado}`}
                      target="_blank"
                      className="w-full text-center px-4 py-2 rounded-lg bg-gray-100 hover:bg-gray-200 text-gray-700 font-medium text-sm"
                    >
                      Validar Autenticidade
                    </a>
                  </>
                )}

                {inscricao.tem_checkin && !temCertificado && (
                  <span className="text-sm text-gray-500 text-center">
                    Certificado em processamento...
                  </span>
                )}

                {podeCancelar && (
                  <button
                    onClick={() => cancelarInscricao(inscricao.id)}
                    disabled={loadingId === inscricao.id}
                    className="w-full px-4 py-2 rounded-lg border border-red-300 text-red-600 hover:bg-red-50 font-medium text-sm disabled:opacity-50"
                  >
                    {loadingId === inscricao.id ? "Cancelando..." : "Cancelar Inscrição"}
                  </button>
                )}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}