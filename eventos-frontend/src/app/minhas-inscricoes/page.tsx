import { getCurrentUser, fetchMinhasInscricoes } from "@/lib/api";
import { redirect } from "next/navigation";
import InscricoesList from "../components/InscricoesList";
import axios from "axios";

export const dynamic = "force-dynamic";

const EVENTOS_URL = process.env.NEXT_PUBLIC_EVENTOS_URL;
const EVENTOS_API_KEY = process.env.NEXT_PUBLIC_EVENTOS_API_KEY;
const CHECKINS_URL = process.env.NEXT_PUBLIC_CHECKINS_URL;
const CHECKINS_API_KEY = process.env.NEXT_PUBLIC_CHECKINS_API_KEY;
const CERTIFICADOS_URL = process.env.NEXT_PUBLIC_CERTIFICADOS_URL;
const CERTIFICADOS_API_KEY = process.env.NEXT_PUBLIC_CERTIFICADOS_API_KEY;

async function fetchEvento(eventoId: string) {
  try {
    const r = await axios.get(`${EVENTOS_URL}/eventos/${eventoId}`, {
      headers: { "x-api-key": EVENTOS_API_KEY },
    });
    return r.data;
  } catch {
    return null;
  }
}

async function fetchCheckin(inscricaoId: string) {
  try {
    const r = await axios.get(`${CHECKINS_URL}/inscricao/${inscricaoId}`, {
      headers: { "x-api-key": CHECKINS_API_KEY },
    });
    return r.data;
  } catch {
    return { tem_checkin: false };
  }
}

async function fetchCertificadoPorInscricao(inscricaoId: string, eventoId: string) {
  try {
    const r = await axios.get(`${CERTIFICADOS_URL}/inscricao/${inscricaoId}/evento/${eventoId}`, {
      headers: { "x-api-key": CERTIFICADOS_API_KEY },
    });
    return r.data;
  } catch {
    return null;
  }
}

export default async function MinhasInscricoesPage() {
  const user = await getCurrentUser();

  if (!user) {
    redirect("/login");
  }

  const inscricoes = await fetchMinhasInscricoes(user.id);

  // Enriquecer dados das inscrições
  const inscricoesEnriquecidas = await Promise.all(
    inscricoes.map(async (inscricao: any) => {
      const [evento, checkinData, certificado] = await Promise.all([
        fetchEvento(inscricao.evento_id),
        fetchCheckin(inscricao.id),
        fetchCertificadoPorInscricao(inscricao.id, inscricao.evento_id),
      ]);

      return {
        ...inscricao,
        evento,
        tem_checkin: checkinData?.tem_checkin || false,
        certificado,
      };
    })
  );

  // Ordenar: eventos futuros primeiro, depois por data
  const agora = new Date();
  inscricoesEnriquecidas.sort((a, b) => {
    const dataA = new Date(a.evento?.inicio_em || 0);
    const dataB = new Date(b.evento?.inicio_em || 0);
    const futuroA = dataA > agora;
    const futuroB = dataB > agora;
    
    if (futuroA && !futuroB) return -1;
    if (!futuroA && futuroB) return 1;
    return dataB.getTime() - dataA.getTime();
  });

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <a href="eventos" className="text-xl font-semibold hover:text-indigo-600">
                Sistema de Eventos
              </a>
            </div>
            <div className="flex items-center space-x-4">
              <a href="eventos" className="text-gray-700 hover:text-gray-900">
                Eventos
              </a>
              <span className="text-indigo-600 font-medium">Minhas Inscrições</span>
              <div className="border-l border-gray-300 h-6"></div>
              <span className="text-sm text-gray-600">{user.nome}</span>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="mb-6">
            <h2 className="text-2xl font-bold text-gray-900">Minhas Inscrições</h2>
            <p className="mt-2 text-sm text-gray-600">
              Acompanhe suas inscrições em eventos, certificados e status de participação.
            </p>
          </div>

          {inscricoesEnriquecidas.length === 0 ? (
            <div className="text-center py-12 bg-white rounded-lg shadow">
              <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
              <h3 className="mt-2 text-sm font-medium text-gray-900">Nenhuma inscrição</h3>
              <p className="mt-1 text-sm text-gray-500">Você ainda não se inscreveu em nenhum evento.</p>
              <div className="mt-6">
                <a href="eventos" className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700">
                  Ver Eventos
                </a>
              </div>
            </div>
          ) : (
            <InscricoesList inscricoes={inscricoesEnriquecidas} />
          )}
        </div>
      </main>
    </div>
  );
}