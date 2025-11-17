import axios from "axios";
import { cookies } from "next/headers";

const SERVICE_API_KEY = process.env.NEXT_PUBLIC_API_KEY || "";

// URLs dos microsserviços
const AUTH_URL = process.env.NEXT_PUBLIC_AUTH_URL || "http://localhost:8001";
const EVENTOS_URL = process.env.NEXT_PUBLIC_EVENTOS_URL || "http://localhost:8002";
const USUARIOS_URL = process.env.NEXT_PUBLIC_USUARIOS_URL || "http://localhost:8003";
const INSCRICOES_URL = process.env.NEXT_PUBLIC_INSCRICOES_URL || "http://localhost:8004";
const INGRESSOS_URL = process.env.NEXT_PUBLIC_INGRESSOS_URL || "http://localhost:8005";
const CHECKINS_URL = process.env.NEXT_PUBLIC_CHECKINS_URL || "http://localhost:8006";
const CERTIFICADOS_URL = process.env.NEXT_PUBLIC_CERTIFICADOS_URL || "http://localhost:8007";

// Cliente API para Server Components
export async function createServerApi() {
  const cookieStore = await cookies();
  const token = cookieStore.get("access_token")?.value;

  const headers: Record<string, string> = {
    "x-api-key": SERVICE_API_KEY,
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  return axios.create({
    headers,
    validateStatus: () => true, // Não lançar erro automaticamente
  });
}

// Cliente API para Client Components (browser)
export function createClientApi(token?: string) {
  const headers: Record<string, string> = {
    "x-api-key": SERVICE_API_KEY,
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  return axios.create({
    headers,
    validateStatus: () => true,
  });
}

// === FUNÇÕES HELPER PARA SERVER COMPONENTS ===

// Buscar usuário atual
export async function getCurrentUser() {
  try {
    const cookieStore = await cookies();
    const token = cookieStore.get("access_token")?.value;
    
    if (!token) return null;

    const api = await createServerApi();
    const response = await api.get(`${AUTH_URL}/me?token=${token}`);
    
    if (response.status === 200) {
      return response.data;
    }
    return null;
  } catch (error) {
    console.error("Erro ao buscar usuário:", error);
    return null;
  }
}

// Buscar eventos públicos
export async function fetchEventosPublicos() {
  try {
    const response = await axios.get(
      `${EVENTOS_URL}/eventos/publicos/ativos`,
      {
        headers: { "x-api-key": SERVICE_API_KEY },
      }
    );
    return response.data;
  } catch (error) {
    console.error("Erro ao buscar eventos:", error);
    return [];
  }
}

// Buscar todos os eventos (requer autenticação)
export async function fetchEventos() {
  try {
    const api = await createServerApi();
    const response = await api.get(`${EVENTOS_URL}/eventos`);
    
    if (response.status === 200) {
      return response.data;
    }
    return [];
  } catch (error) {
    console.error("Erro ao buscar eventos:", error);
    return [];
  }
}

// Buscar evento específico
export async function fetchEvento(id: string) {
  try {
    const api = await createServerApi();
    const response = await api.get(`${EVENTOS_URL}/eventos/${id}`);
    
    if (response.status === 200) {
      return response.data;
    }
    return null;
  } catch (error) {
    console.error("Erro ao buscar evento:", error);
    return null;
  }
}

// Buscar inscrições do usuário
export async function fetchMinhasInscricoes(usuarioId: string) {
  try {
    const api = await createServerApi();
    const response = await api.get(`${INSCRICOES_URL}/usuario/${usuarioId}`);
    
    if (response.status === 200) {
      return response.data;
    }
    return [];
  } catch (error) {
    console.error("Erro ao buscar inscrições:", error);
    return [];
  }
}

// Buscar certificados do usuário
export async function fetchMeusCertificados() {
  try {
    const api = await createServerApi();
    const response = await api.get(`${CERTIFICADOS_URL}/meus`);
    
    if (response.status === 200) {
      return response.data;
    }
    return [];
  } catch (error) {
    console.error("Erro ao buscar certificados:", error);
    return [];
  }
}

// Verificar se usuário tem check-in em um evento
export async function verificarCheckin(inscricaoId: string) {
  try {
    const api = await createServerApi();
    const response = await api.get(`${CHECKINS_URL}/inscricao/${inscricaoId}`);
    
    if (response.status === 200) {
      return response.data;
    }
    return { tem_checkin: false };
  } catch (error) {
    console.error("Erro ao verificar check-in:", error);
    return { tem_checkin: false };
  }
}

// Exportar URLs para uso em rotas API
export const API_URLS = {
  AUTH: AUTH_URL,
  EVENTOS: EVENTOS_URL,
  USUARIOS: USUARIOS_URL,
  INSCRICOES: INSCRICOES_URL,
  INGRESSOS: INGRESSOS_URL,
  CHECKINS: CHECKINS_URL,
  CERTIFICADOS: CERTIFICADOS_URL,
};