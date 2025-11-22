import { getCurrentUser, fetchEventos, fetchMinhasInscricoes } from "@/lib/api";
import { redirect } from "next/navigation";
import EventosList from "../components/EventosList";

export const dynamic = "force-dynamic";

export default async function EventosPage() {
  const user = await getCurrentUser();
  
  if (!user) {
    redirect("/login");
  }

  const [eventos, inscricoes] = await Promise.all([
    fetchEventos(),
    fetchMinhasInscricoes(user.id),
  ]);

  const eventosDisponiveis = eventos.filter((evento: any) => {
    const dataInicio = new Date(evento.inicio_em);
    const agora = new Date();
    return dataInicio > agora;
  });

  const eventosInscritosIds = new Set(
    inscricoes
      .filter((i: any) => i.status === "ativa")
      .map((i: any) => i.evento_id)
  );

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-semibold">Sistema de Eventos</h1>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-indigo-600 font-medium">Eventos</span>
              <a href="minhas-inscricoes" className="text-gray-700 hover:text-gray-900">
                Minhas Inscrições
              </a>
              <div className="border-l border-gray-300 h-6"></div>
              <span className="text-sm text-gray-600">{user.nome}</span>
              <form action="/api/session" method="DELETE">
                <button type="submit" className="text-sm text-red-600 hover:text-red-800">
                  Sair
                </button>
              </form>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        {user.papel === "rapido" && (
          <div className="mb-6 bg-yellow-50 border-l-4 border-yellow-400 p-4">
            <div className="flex">
              <div className="ml-3">
                <p className="text-sm text-yellow-700">
                  Você ainda não completou seu cadastro.{" "}
                  <a href="completar-cadastro" className="font-medium underline hover:text-yellow-600">
                    Clique aqui para completar
                  </a>
                </p>
              </div>
            </div>
          </div>
        )}

        <div className="px-4 py-6 sm:px-0">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Eventos Disponíveis</h2>

          {eventosDisponiveis.length === 0 ? (
            <div className="text-center py-12 bg-white rounded-lg shadow">
              <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
              </svg>
              <p className="mt-4 text-gray-500">Nenhum evento disponível no momento.</p>
              <p className="mt-2 text-sm text-gray-400">
                {eventos.length > 0 
                  ? `Existem ${eventos.length} eventos cadastrados, mas nenhum está ativo.`
                  : "Nenhum evento foi cadastrado ainda."}
              </p>
            </div>
          ) : (
            <EventosList
              eventos={eventosDisponiveis}
              eventosInscritosIds={eventosInscritosIds}
              usuarioId={user.id}
              inscricoes={inscricoes}
            />
          )}
        </div>
      </main>
    </div>
  );
}