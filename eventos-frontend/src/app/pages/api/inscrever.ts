// pages/api/inscrever.ts
import type { NextApiRequest, NextApiResponse } from "next";
import { createServerApi } from "../../lib/api";

export default async function handler(req: NextApiRequest, res: NextApiResponse){
  if (req.method !== "POST") return res.status(405).end();
  const { evento_id, usuario_id } = req.body;
  try {
    const api = createServerApi(req);
    const r = await api.post(`${process.env.NEXT_PUBLIC_INSCRICOES_URL}/`, null, {
      params: { evento_id, usuario_id } // conforme sua rota /?evento_id=...
    });
    return res.status(201).json(r.data);
  } catch (err: any) {
    const status = err?.response?.status || 500;
    return res.status(status).json(err?.response?.data || { message: err.message });
  }
}
