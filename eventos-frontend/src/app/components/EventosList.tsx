"use client";

import { useState } from "react";
import axios from "axios";

export default function EventosList({ eventos, eventosInscritosIds, usuarioId }: any) {
  const [loadingId, setLoadingId] = useState<string | null>(null);

  async function inscrever(eventoId: string) {
    try {
      setLoadingId(eventoId);

      const r = await axios.post("/app/api/inscrever", {
        evento_id: eventoId,
        usuario_id: usuarioId,
      });

      if (r.status === 201) {
        alert("Inscrição realizada com sucesso!");
        window.location.reload();
      } else {
        alert("Erro ao inscrever. Tente novamente.");
      }
    } catch (err: any) {
      console.error(err);
      alert("Erro ao inscrever.");
    } finally {
      setLoadingId(null);
    }
  }

  return (
    <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
      {eventos.map((ev: any) => {
        const inscrito = eventosInscritosIds.has(ev.id);
        const data = new Date(ev.data_inicio).toLocaleDateString("pt-BR", {
          day: "2-digit",
          month: "long",
          year: "numeric",
        });

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
  );
}
