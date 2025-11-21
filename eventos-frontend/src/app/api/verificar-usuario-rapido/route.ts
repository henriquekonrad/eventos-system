import { NextRequest, NextResponse } from "next/server";
import axios from "axios";

const AUTH_URL = process.env.NEXT_PUBLIC_AUTH_URL;
const AUTH_API_KEY = process.env.NEXT_PUBLIC_AUTH_API_KEY;

export async function GET(req: NextRequest) {
  const { searchParams } = new URL(req.url);
  const email = searchParams.get("email");

  if (!email) {
    return NextResponse.json(
      { message: "Email é obrigatório" },
      { status: 400 }
    );
  }

  try {
    const response = await axios.get(
      `${AUTH_URL}/verificar-usuario-rapido?email=${encodeURIComponent(email)}`,
      {
        headers: { "x-api-key": AUTH_API_KEY },
        timeout: 10000
      }
    );

    if (response.status === 200) {
      return NextResponse.json(response.data);
    }

    return NextResponse.json(
      { isRapido: false },
      { status: 200 }
    );
  } catch (error: any) {
    console.error("Erro ao verificar usuário rápido:", error);
    return NextResponse.json(
      { isRapido: false },
      { status: 200 }
    );
  }
}