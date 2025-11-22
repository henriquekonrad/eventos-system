"use client";

import { useState } from "react";
import axios from "axios";

export default function EventosList({ 
  eventos, 
  eventosInscritosIds, 
  usuarioId,
  inscricoes = []
}: any) {
  const [loadingId, setLoadingId] = useState<string | null>(null);
  const [cancelingId, setCancelingId] = useState<string | null>(null);
  const [inscritosState, setInscritosState] = useState<Set<string>>(new Set(eventosInscritosIds));
  const [error, setError] = useState<string>("");

  // Criar mapa de evento_id para inscricao_id
  const eventoParaInscricao: Record<string, string> = {};
  inscricoes.forEach((i: any) => {
    if (i.status === "ativa") {
      eventoParaInscricao[i.evento_id] = i.id;
    }
  });

  async function inscrever(eventoId: string) {
    try {
      setLoadingId(eventoId);
      setError("");
      
      const r = await axios.post("/api/inscrever", {
        evento_id: eventoId,
        usuario_id: usuarioId,
      });

      if (r.status === 201) {
        setInscritosState(prev => new Set(prev).add(eventoId));
        alert("Inscrição realizada com sucesso!");
        window.location.reload();
      } else {
        setError(r.data?.message || "Erro ao inscrever");
        alert(`Erro: ${r.data?.message || "Erro ao inscrever. Tente novamente."}`);
      }
    } catch (err: any) {
      const errorMsg = err.response?.data?.message || err.response?.data?.detail || "Erro ao conectar com o servidor";
      setError(errorMsg);
      alert(`Erro: ${errorMsg}`);
    } finally {
      setLoadingId(null);
    }
  }

  async function cancelarInscricao(eventoId: string) {
    const inscricaoId = eventoParaInscricao[eventoId];
    if (!inscricaoId) {
      alert("Inscrição não encontrada");
      return;
    }

    if (!confirm("Tem certeza que deseja cancelar esta inscrição?")) return;

    setCancelingId(eventoId);
    try {
      const r = await axios.post("/api/cancelar-inscricao", { inscricao_id: inscricaoId });
      
      if (r.data.ok) {
        setInscritosState(prev => {
          const newSet = new Set(prev);
          newSet.delete(eventoId);
          return newSet;
        });
        alert("Inscrição cancelada com sucesso!");
      }
    } catch (err: any) {
      const msg = err.response?.data?.message || "Erro ao cancelar inscrição";
      alert(`Erro: ${msg}`);
    } finally {
      setCancelingId(null);
    }
  }

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

  return (
    <>
      {error && (
        <div className="mb-4 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {eventos.map((ev: any) => {
          const inscrito = inscritosState.has(ev.id);
          const data = formatarData(ev.inicio_em);
          const podeCancelar = inscrito && eventoParaInscricao[ev.id];

          return (
            <div
              key={ev.id}
              className="bg-white shadow-md rounded-xl p-6 border border-gray-200 hover:shadow-lg transition-shadow"
            >
              <h3 className="text-xl font-semibold text-gray-900">{ev.titulo}</h3>
              <p className="mt-2 text-gray-600 line-clamp-3">{ev.descricao}</p>
              
              <div className="mt-4 text-sm text-gray-700 space-y-1">
                <p><span className="font-medium">Data:</span> {data}</p>
                {ev.local && <p><span className="font-medium">Local:</span> {ev.local}</p>}
              </div>

              <div className="mt-6 space-y-2">
                {inscrito ? (
                  <>
                    <span className="inline-flex w-full justify-center px-3 py-2 rounded-lg bg-green-100 text-green-700 text-sm font-medium">
                      ✔ Já inscrito
                    </span>
                    {podeCancelar && (
                      <button
                        onClick={() => cancelarInscricao(ev.id)}
                        disabled={cancelingId === ev.id}
                        className="w-full px-4 py-2 rounded-lg border border-red-300 text-red-600 hover:bg-red-50 text-sm font-medium disabled:opacity-50"
                      >
                        {cancelingId === ev.id ? "Cancelando..." : "Cancelar Inscrição"}
                      </button>
                    )}
                  </>
                ) : (
                  <button
                    onClick={() => inscrever(ev.id)}
                    disabled={loadingId === ev.id}
                    className={`w-full px-4 py-2 rounded-lg text-white font-medium 
                      ${loadingId === ev.id ? "bg-indigo-400" : "bg-indigo-600 hover:bg-indigo-700"}`}
                  >
                    {loadingId === ev.id ? "Inscrevendo..." : "Inscrever-se"}
                  </button>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </>
  );
}