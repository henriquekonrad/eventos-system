import { NextRequest, NextResponse } from "next/server";
import { createServerApi } from "@/lib/api";

export async function POST(req: NextRequest) {
  const body = await req.json();
  const { evento_id, usuario_id } = body;

  try {
    const api = createServerApi(req);
    const r = await api.post(
      `${process.env.NEXT_PUBLIC_INSCRICOES_URL}/`,
      null,
      { params: { evento_id, usuario_id } }
    );
    return NextResponse.json(r.data, { status: 201 });
  } catch (err: any) {
    return NextResponse.json(
      err.response?.data || { message: "Erro" },
      { status: err.response?.status || 500 }
    );
  }
}
