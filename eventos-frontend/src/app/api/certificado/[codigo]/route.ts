import { NextRequest, NextResponse } from "next/server";
import axios from "axios";

const CERTIFICADOS_URL = process.env.NEXT_PUBLIC_CERTIFICADOS_URL;
const CERTIFICADOS_API_KEY = process.env.NEXT_PUBLIC_CERTIFICADOS_API_KEY;

export async function GET(
  req: NextRequest,
  { params }: { params: Promise<{ codigo: string }> }
) {
  const { codigo } = await params;
  
  console.log("=== API ROUTE: BUSCANDO CERTIFICADO ===");
  console.log("Código:", codigo);
  console.log("CERTIFICADOS_URL:", CERTIFICADOS_URL);
  console.log("API_KEY existe:", !!CERTIFICADOS_API_KEY);
  console.log("API_KEY primeiros chars:", CERTIFICADOS_API_KEY?.substring(0, 5) + "...");

  if (!codigo) {
    return NextResponse.json(
      { message: "Código é obrigatório" },
      { status: 400 }
    );
  }

  try {
    const url = `${CERTIFICADOS_URL}/codigo/${codigo}`;
    console.log("URL da requisição:", url);

    const response = await axios.get(url, {
      headers: {
        "x-api-key": CERTIFICADOS_API_KEY || "",
        "Content-Type": "application/json"
      },
      timeout: 10000
    });

    console.log("✅ Sucesso! Status:", response.status);
    return NextResponse.json(response.data);

  } catch (error: any) {
    console.error("❌ Erro na requisição:");
    console.error("Status:", error.response?.status);
    console.error("Data:", error.response?.data);
    console.error("Message:", error.message);

    if (error.response?.status === 404) {
      return NextResponse.json(
        { message: "Certificado não encontrado" },
        { status: 404 }
      );
    }

    return NextResponse.json(
      { 
        message: error.response?.data?.detail || "Erro ao buscar certificado",
        debug: {
          status: error.response?.status,
          url: `${CERTIFICADOS_URL}/codigo/${codigo}`,
          hasApiKey: !!CERTIFICADOS_API_KEY
        }
      },
      { status: error.response?.status || 500 }
    );
  }
}