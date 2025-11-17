import axios from "axios";
import cookie from "cookie";

const SERVICE_API_KEY = process.env.NEXT_PUBLIC_API_KEY;
const EVENTOS_URL = process.env.NEXT_PUBLIC_EVENTOS_URL;

export function createServerApi(req?: any) {
  const headers: any = { "x-api-key": SERVICE_API_KEY };

  if (req?.headers?.get("cookie")) {
    const cookies = cookie.parse(req.headers.get("cookie"));
    if (cookies.access_token) {
      headers["Authorization"] = `Bearer ${cookies.access_token}`;
    }
  }

  return axios.create({ headers });
}

// Server Component friendly
export async function fetchEventosServer() {
  const api = axios.create({ headers: { "x-api-key": SERVICE_API_KEY } });
  const r = await api.get(`${EVENTOS_URL}/eventos`);
  return r.data;
}
