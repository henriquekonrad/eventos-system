import { NextRequest, NextResponse } from "next/server";
import { cookies } from "next/headers";
import axios from "axios";

const INSCRICOES_URL = process.env.NEXT_PUBLIC_INSCRICOES_URL;
const INSCRICOES_API_KEY = process.env.NEXT_PUBLIC_INSCRICOES_API_KEY;
const CHECKINS_URL = process.env.NEXT_PUBLIC_CHECKINS_URL;
const CHECKINS_API_KEY = process.env.NEXT_PUBLIC_CHECKINS_API_KEY;
const AUTH_URL = process.env.NEXT_PUBLIC_AUTH_URL;
const AUTH_API_KEY = process.env.NEXT_PUBLIC_AUTH_API_KEY;

export async function POST(req: NextRequest) {
  try {
    const cookieStore = await cookies();
    const token = cookieStore.get("access_token")?.value;

    if (!token) {
      return NextResponse.json(
        { message: "Não autenticado" },
        { status: 401 }
      );
    }

    // Buscar usuário atual
    const userResponse = await axios.get(
      `${AUTH_URL}/me?token=${token}`,
      { headers: { "x-api-key": AUTH_API_KEY }, timeout: 10000 }
    );

    if (userResponse.status !== 200) {
      return NextResponse.json(
        { message: "Usuário não encontrado" },
        { status: 401 }
      );
    }

    const userId = userResponse.data.id;
    const { inscricao_id } = await req.json();

    if (!inscricao_id) {
      return NextResponse.json(
        { message: "ID da inscrição é obrigatório" },
        { status: 400 }
      );
    }

    // Buscar inscrição para verificar se pertence ao usuário
    const inscricaoResponse = await axios.get(
      `${INSCRICOES_URL}/${inscricao_id}`,
      { headers: { "x-api-key": INSCRICOES_API_KEY }, timeout: 10000 }
    );

    if (inscricaoResponse.status !== 200) {
      return NextResponse.json(
        { message: "Inscrição não encontrada" },
        { status: 404 }
      );
    }

    const inscricao = inscricaoResponse.data;

    // Verificar se a inscrição pertence ao usuário
    if (inscricao.usuario_id !== userId) {
      return NextResponse.json(
        { message: "Você não tem permissão para cancelar esta inscrição" },
        { status: 403 }
      );
    }

    // Verificar se já tem check-in
    try {
      const checkinResponse = await axios.get(
        `${CHECKINS_URL}/inscricao/${inscricao_id}`,
        { headers: { "x-api-key": CHECKINS_API_KEY }, timeout: 10000 }
      );

      if (checkinResponse.data?.tem_checkin) {
        return NextResponse.json(
          { message: "Não é possível cancelar inscrição com check-in realizado" },
          { status: 400 }
        );
      }
    } catch (err) {
      // Se erro ao verificar check-in, continuar (provavelmente não tem)
      console.log("Erro ao verificar check-in, continuando...");
    }

    // Cancelar inscrição
    const cancelResponse = await axios.patch(
      `${INSCRICOES_URL}/${inscricao_id}/cancelar`,
      {},
      {
        headers: {
          "x-api-key": INSCRICOES_API_KEY,
          "Authorization": `Bearer ${token}`
        },
        timeout: 10000
      }
    );

    if (cancelResponse.status === 200) {
      return NextResponse.json({
        ok: true,
        message: "Inscrição cancelada com sucesso"
      });
    }

    return NextResponse.json(
      { message: "Erro ao cancelar inscrição" },
      { status: cancelResponse.status }
    );

  } catch (error: any) {
    console.error("Erro ao cancelar inscrição:", error);
    return NextResponse.json(
      { message: error.response?.data?.detail || "Erro ao cancelar inscrição" },
      { status: error.response?.status || 500 }
    );
  }
}