// pages/api/session.ts
import type { NextApiRequest, NextApiResponse } from "next";
import axios from "axios";
import cookie from "cookie";

const AUTH_URL = process.env.NEXT_PUBLIC_AUTH_URL;
const SERVICE_API_KEY = process.env.NEXT_PUBLIC_API_KEY;

export default async function handler(req: NextApiRequest, res: NextApiResponse){
  if (req.method === "POST") {
    const { email, senha } = req.body;
    try {
      // chama auth-service /login — supondo que ele retorna { access_token, token_type }
      const r = await axios.post(
        `${AUTH_URL}/login`,
        { email, senha },
        { headers: { "x-api-key": SERVICE_API_KEY } }
      );
      const token = r.data?.access_token;
      if (!token) return res.status(500).json({ message: "Auth sem token" });

      // set cookie HttpOnly (duração 45 dias como no seu auth-service)
      res.setHeader("Set-Cookie", cookie.serialize("access_token", token, {
        httpOnly: true,
        secure: process.env.NODE_ENV === "production",
        maxAge: 60 * 60 * 24 * 45,
        sameSite: "lax",
        path: "/"
      }));

      return res.status(200).json({ ok: true });
    } catch (err: any) {
      const status = err?.response?.status || 500;
      const data = err?.response?.data || { message: err.message };
      return res.status(status).json(data);
    }
  }

  if (req.method === "DELETE") {
    // logout: remove cookie
    res.setHeader("Set-Cookie", cookie.serialize("access_token", "", {
      httpOnly: true, secure: process.env.NODE_ENV === "production",
      maxAge: 0, path: "/", sameSite: "lax"
    }));
    return res.status(200).json({ ok: true });
  }

  res.setHeader("Allow", ["POST", "DELETE"]);
  res.status(405).end("Method not allowed");
}
