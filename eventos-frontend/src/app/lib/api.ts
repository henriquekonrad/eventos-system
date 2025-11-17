// lib/api.ts
import axios, { AxiosInstance } from "axios";
import cookie from "cookie";

// URLs
const SERVICE_API_KEY = process.env.NEXT_PUBLIC_API_KEY;
const AUTH_URL = process.env.NEXT_PUBLIC_AUTH_URL;
const EVENTOS_URL = process.env.NEXT_PUBLIC_EVENTOS_URL;

export function createServerApi(req?: any): AxiosInstance {
  const headers: any = { "x-api-key": SERVICE_API_KEY };
  if (req?.headers?.cookie) {
    const cookies = cookie.parse(req.headers.cookie || "");
    if (cookies.access_token) headers["Authorization"] = `Bearer ${cookies.access_token}`;
  }
  return axios.create({ headers });
}

// Exemplo de chamada para eventos usando server-side API
export async function fetchEventosServer(req?: any){
  const api = createServerApi(req);
  const res = await api.get(`${EVENTOS_URL}/eventos`);
  return res.data;
}
