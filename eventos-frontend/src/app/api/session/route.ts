import { NextRequest, NextResponse } from "next/server";
import axios from "axios";
import cookie from "cookie";

const AUTH_URL = process.env.NEXT_PUBLIC_AUTH_URL;
const SERVICE_API_KEY = process.env.NEXT_PUBLIC_AUTH_API_KEY;

export async function POST(req: NextRequest) {
  console.log("=== INICIO LOGIN ===");
  console.log("AUTH_URL:", AUTH_URL);
  console.log("API_KEY exists:", !!SERVICE_API_KEY);
  console.log("API_KEY length:", SERVICE_API_KEY?.length);

  const { email, senha } = await req.json();
  console.log("Email recebido:", email);
  console.log("Senha recebida:", senha ? "***" : "vazia");

  try {
    const loginUrl = `${AUTH_URL}/login`;
    console.log("Fazendo request para:", loginUrl);
    console.log("Headers:", {
      "Content-Type": "application/json",
      "x-api-key": SERVICE_API_KEY ? "***" : "VAZIO",
    });
    console.log("Body:", { email, senha: "***" });

    const r = await axios.post(
      loginUrl,
      { email, senha },
      { 
        headers: { 
          "Content-Type": "application/json",
          "x-api-key": SERVICE_API_KEY 
        },
        timeout: 10000 // 10 segundos
      }
    );

    console.log("✅ Login bem-sucedido!");
    console.log("Status:", r.status);
    console.log("Data:", r.data);

    const token = r.data?.access_token;

    if (!token) {
      console.error("❌ Token não encontrado na resposta");
      return NextResponse.json(
        { message: "Token não recebido do servidor" },
        { status: 500 }
      );
    }

    // Buscar dados do usuário
    console.log("Buscando dados do usuário...");
    try {
      const userResponse = await axios.get(
        `${AUTH_URL}/me?token=${token}`,
        { 
          headers: { "x-api-key": SERVICE_API_KEY },
          timeout: 10000
        }
      );

      console.log("✅ Dados do usuário:", userResponse.data);
      const userData = userResponse.data;
      const requiresCompletion = !userData.nome || userData.nome.trim() === "";

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

      console.log("=== LOGIN COMPLETO ===");
      return res;

    } catch (userErr: any) {
      console.error("❌ Erro ao buscar usuário:", userErr.response?.data || userErr.message);
      
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
    console.error("=== ERRO NO LOGIN ===");
    console.error("Erro completo:", err);
    console.error("Response status:", err.response?.status);
    console.error("Response data:", err.response?.data);
    console.error("Error message:", err.message);
    console.error("Request config:", {
      url: err.config?.url,
      method: err.config?.method,
      headers: err.config?.headers,
    });
    
    const errorMessage = err.response?.data?.detail || 
                        err.response?.data?.message || 
                        err.message || 
                        "Erro ao fazer login";

    return NextResponse.json(
      { message: errorMessage },
      { status: err.response?.status || 500 }
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
