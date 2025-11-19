"use client";

import { useState } from "react";
import axios from "axios";

export default function EventosList({ 
  eventos, 
  eventosInscritosIds, 
  usuarioId 
}: any) {
  const [loadingId, setLoadingId] = useState<string | null>(null);
  const [error, setError] = useState<string>("");

  async function inscrever(eventoId: string) {
    try {
      setLoadingId(eventoId);
      setError("");
      
      console.log("📝 Tentando inscrever no evento:", eventoId);
      console.log("👤 Usuário ID:", usuarioId);

      const r = await axios.post("/api/inscrever", {
        evento_id: eventoId,
        usuario_id: usuarioId,
      });

      console.log("✅ Resposta:", r.status, r.data);

      if (r.status === 201) {
        alert("Inscrição realizada com sucesso!");
        window.location.reload();
      } else {
        console.error("❌ Status inesperado:", r.status, r.data);
        setError(r.data?.message || "Erro ao inscrever");
        alert(`Erro: ${r.data?.message || "Erro ao inscrever. Tente novamente."}`);
      }
    } catch (err: any) {
      console.error("❌ Erro ao inscrever:", err);
      console.error("Response:", err.response?.data);
      
      const errorMsg = err.response?.data?.message || 
                      err.response?.data?.detail || 
                      "Erro ao conectar com o servidor";
      
      setError(errorMsg);
      alert(`Erro: ${errorMsg}`);
    } finally {
      setLoadingId(null);
    }
  }

  function formatarData(dataString: string) {
    try {
      const data = new Date(dataString);
      
      // Verificar se a data é válida
      if (isNaN(data.getTime())) {
        console.error("Data inválida:", dataString);
        return "Data não disponível";
      }

      return data.toLocaleDateString("pt-BR", {
        day: "2-digit",
        month: "long",
        year: "numeric",
      });
    } catch (error) {
      console.error("Erro ao formatar data:", error);
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
          const inscrito = eventosInscritosIds.has(ev.id);
          
          // CORRIGIDO: usar inicio_em em vez de data_inicio
          const data = formatarData(ev.inicio_em);

          return (
            <div
              key={ev.id}
              className="bg-white shadow-md rounded-xl p-6 border border-gray-200 hover:shadow-lg transition-shadow"
            >
              <h3 className="text-xl font-semibold text-gray-900">{ev.titulo}</h3>
              <p className="mt-2 text-gray-600 line-clamp-3">{ev.descricao}</p>
              
              <div className="mt-4 text-sm text-gray-700 space-y-1">
                <p>
                  <span className="font-medium">Data:</span> {data}
                </p>
                {ev.local && (
                  <p>
                    <span className="font-medium">Local:</span> {ev.local}
                  </p>
                )}
              </div>

              <div className="mt-6">
                {inscrito ? (
                  <span className="inline-flex px-3 py-2 rounded-lg bg-green-100 text-green-700 text-sm font-medium">
                    ✔ Já inscrito
                  </span>
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