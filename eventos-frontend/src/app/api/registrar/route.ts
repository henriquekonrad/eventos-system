import { NextRequest, NextResponse } from "next/server";
import axios from "axios";

const AUTH_URL = process.env.NEXT_PUBLIC_AUTH_URL;
const AUTH_API_KEY = process.env.NEXT_PUBLIC_AUTH_API_KEY;

export async function POST(req: NextRequest) {
  console.log("=== INICIO REGISTRO ===");

  const { nome, email, cpf, senha } = await req.json();

  // Validações básicas
  if (!nome || !email || !cpf || !senha) {
    return NextResponse.json(
      { message: "Todos os campos são obrigatórios" },
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
    const registerUrl = `${AUTH_URL}/registrar`;
    console.log("Fazendo request para:", registerUrl);

    const response = await axios.post(
      registerUrl,
      { 
        nome, 
        email, 
        cpf, 
        senha,
        papel: "participante" // Novo usuário sempre começa como participante
      },
      { 
        headers: { 
          "Content-Type": "application/json",
          "x-api-key": AUTH_API_KEY 
        },
        timeout: 10000
      }
    );

    console.log("✅ Registro bem-sucedido!");
    console.log("Status:", response.status);

    return NextResponse.json({ 
      ok: true,
      message: "Cadastro realizado com sucesso!",
      user: response.data
    });

  } catch (err: any) {
    console.error("=== ERRO NO REGISTRO ===");
    console.error("Response status:", err.response?.status);
    console.error("Response data:", err.response?.data);
    
    const errorMessage = err.response?.data?.detail || 
                        err.response?.data?.message || 
                        err.message || 
                        "Erro ao fazer cadastro";

    return NextResponse.json(
      { message: errorMessage },
      { status: err.response?.status || 500 }
    );
  }
}