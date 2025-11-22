import { NextRequest, NextResponse } from "next/server";
import axios from "axios";

const AUTH_URL = process.env.NEXT_PUBLIC_AUTH_URL;
const AUTH_API_KEY = process.env.NEXT_PUBLIC_AUTH_API_KEY;

export async function POST(req: NextRequest) {
  console.log("=== INICIO CADASTRAR SENHA RAPIDO ===");

  const { email, nome, cpf, senha } = await req.json();

  if (!email || !nome || !senha) {
    return NextResponse.json(
      { message: "Email, nome e senha são obrigatórios" },
      { status: 400 }
    );
  }

  if (senha.length < 6) {
    return NextResponse.json(
      { message: "A senha deve ter no mínimo 6 caracteres" },
      { status: 400 }
    );
  }

  try {
    const response = await axios.post(
      `${AUTH_URL}/cadastrar-senha-rapido`,
      { 
        email,
        nome, 
        cpf, 
        senha
      },
      { 
        headers: { 
          "Content-Type": "application/json",
          "x-api-key": AUTH_API_KEY 
        },
        timeout: 10000
      }
    );

    console.log("✅ Senha cadastrada com sucesso!");

    return NextResponse.json({ 
      ok: true,
      message: "Senha cadastrada com sucesso!",
      user: response.data
    });

  } catch (err: any) {
    console.error("=== ERRO AO CADASTRAR SENHA ===");
    console.error("Response status:", err.response?.status);
    console.error("Response data:", err.response?.data);
    
    const errorMessage = err.response?.data?.detail || 
                        err.response?.data?.message || 
                        err.message || 
                        "Erro ao cadastrar senha";

    return NextResponse.json(
      { message: errorMessage },
      { status: err.response?.status || 500 }
    );
  }
}