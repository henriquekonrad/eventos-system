import { NextRequest, NextResponse } from "next/server";
import axios from "axios";
import cookie from "cookie";

const AUTH_URL = process.env.NEXT_PUBLIC_AUTH_URL;
const SERVICE_API_KEY = process.env.NEXT_PUBLIC_AUTH_API_KEY;

export async function POST(req: NextRequest) {
  const { email, senha } = await req.json();

  try {
    // Login no microsserviço
    const r = await axios.post(
      `${AUTH_URL}/login`,
      { email, senha },
      { headers: { "x-api-key": SERVICE_API_KEY } }
    );

    const token = r.data?.access_token;

    if (!token) {
      return NextResponse.json(
        { message: "Token não recebido do servidor" },
        { status: 500 }
      );
    }

    // Buscar dados do usuário para verificar se precisa completar cadastro
    try {
      const userResponse = await axios.get(
        `${AUTH_URL}/me?token=${token}`,
        { headers: { "x-api-key": SERVICE_API_KEY } }
      );

      const userData = userResponse.data;
      const requiresCompletion = !userData.nome || userData.nome.trim() === "";

      // Criar resposta com cookie
      const res = NextResponse.json({ 
        ok: true,
        requiresCompletion,
        user: userData
      });

      res.headers.set(
        "Set-Cookie",
        cookie.serialize("access_token", token, {
          httpOnly: true,
          secure: process.env.NODE_ENV === "production",
          maxAge: 60 * 60 * 24 * 45,
          sameSite: "lax",
          path: "/",
        })
      );

      return res;
    } catch (userErr) {
      // Se falhar ao buscar usuário, logar mas continuar
      console.error("Erro ao buscar dados do usuário:", userErr);
      
      const res = NextResponse.json({ 
        ok: true,
        requiresCompletion: false
      });

      res.headers.set(
        "Set-Cookie",
        cookie.serialize("access_token", token, {
          httpOnly: true,
          secure: process.env.NODE_ENV === "production",
          maxAge: 60 * 60 * 24 * 45,
          sameSite: "lax",
          path: "/",
        })
      );

      return res;
    }

  } catch (err: any) {
    console.error("Erro no login:", err.response?.data || err.message);
    const errorMessage = err.response?.data?.detail || 
                        err.response?.data?.message || 
                        err.message || 
                        "Erro ao fazer login";

    return NextResponse.json(
      { message: errorMessage },  // ✅ Sempre uma string
      { status: err.response?.status || 401 }
    );
  }
}

export async function DELETE() {
  const res = NextResponse.json({ ok: true });
  res.headers.set(
    "Set-Cookie",
    cookie.serialize("access_token", "", {
      httpOnly: true,
      secure: process.env.NODE_ENV === "production",
      maxAge: 0,
      sameSite: "lax",
      path: "/",
    })
  );
  return res;
}