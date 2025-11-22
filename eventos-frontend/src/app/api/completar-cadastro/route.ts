import { NextRequest, NextResponse } from "next/server";
import { cookies } from "next/headers";
import axios from "axios";

const AUTH_URL = process.env.NEXT_PUBLIC_AUTH_URL;
const AUTH_API_KEY = process.env.NEXT_PUBLIC_AUTH_API_KEY;

export async function PATCH(req: NextRequest) {
  try {
    const cookieStore = await cookies();
    const token = cookieStore.get("access_token")?.value;

    if (!token) {
      return NextResponse.json(
        { message: "Não autenticado" },
        { status: 401 }
      );
    }

    const body = await req.json();
    const { nome, cpf, senha } = body;

    // Buscar dados atuais do usuário
    const meResponse = await axios.get(
      `${AUTH_URL}/me?token=${token}`,
      {
        headers: { "x-api-key": AUTH_API_KEY },
        timeout: 10000
      }
    );

    if (meResponse.status !== 200) {
      return NextResponse.json(
        { message: "Erro ao buscar usuário" },
        { status: 401 }
      );
    }

    const userData = meResponse.data;

    // Verificar se é usuário rápido
    if (userData.papel !== "rapido") {
      return NextResponse.json(
        { message: "Apenas usuários rápidos podem completar cadastro" },
        { status: 403 }
      );
    }

    // Atualizar dados do usuário
    const updateResponse = await axios.patch(
      `${AUTH_URL}/completar-cadastro`,
      {
        nome,
        cpf,
        senha
      },
      {
        headers: {
          "Content-Type": "application/json",
          "x-api-key": AUTH_API_KEY,
          "Authorization": `Bearer ${token}`
        },
        timeout: 10000
      }
    );

    if (updateResponse.status === 200) {
      return NextResponse.json({
        ok: true,
        message: "Cadastro completado com sucesso!",
        user: updateResponse.data
      });
    }

    return NextResponse.json(
      { message: "Erro ao completar cadastro" },
      { status: updateResponse.status }
    );

  } catch (error: any) {
    console.error("Erro ao completar cadastro:", error);
    return NextResponse.json(
      { message: error.response?.data?.detail || "Erro ao completar cadastro" },
      { status: error.response?.status || 500 }
    );
  }
}