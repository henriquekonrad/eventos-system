import { NextRequest, NextResponse } from "next/server";
import { cookies } from "next/headers";
import axios from "axios";

const AUTH_URL = process.env.NEXT_PUBLIC_AUTH_URL;
const AUTH_API_KEY = process.env.NEXT_PUBLIC_AUTH_API_KEY;

export async function GET(req: NextRequest) {
  try {
    const cookieStore = await cookies();
    const token = cookieStore.get("access_token")?.value;

    if (!token) {
      return NextResponse.json(
        { message: "Não autenticado" },
        { status: 401 }
      );
    }

    const response = await axios.get(
      `${AUTH_URL}/me?token=${token}`,
      {
        headers: { "x-api-key": AUTH_API_KEY },
        timeout: 10000
      }
    );

    if (response.status === 200) {
      return NextResponse.json(response.data);
    }

    return NextResponse.json(
      { message: "Erro ao buscar usuário" },
      { status: response.status }
    );
  } catch (error: any) {
    console.error("Erro ao buscar usuário:", error);
    return NextResponse.json(
      { message: error.response?.data?.detail || "Erro ao buscar usuário" },
      { status: error.response?.status || 500 }
    );
  }
}