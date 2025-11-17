import { NextRequest, NextResponse } from "next/server";
import axios from "axios";
import cookie from "cookie";

const AUTH_URL = process.env.NEXT_PUBLIC_AUTH_URL;
const SERVICE_API_KEY = process.env.NEXT_PUBLIC_API_KEY;

export async function POST(req: NextRequest) {
  const { email, senha } = await req.json();

  try {
    const r = await axios.post(
      `${AUTH_URL}/login`,
      { email, senha },
      { headers: { "x-api-key": SERVICE_API_KEY } }
    );

    const token = r.data?.access_token;

    const res = NextResponse.json({ ok: true });
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
  } catch (err: any) {
    return NextResponse.json(
      { message: err?.response?.data || "Erro" },
      { status: 401 }
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
