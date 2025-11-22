import CertificadoView from "./CertificadoView";

async function fetchCertificado(codigo: string) {
  console.log("=== BUSCANDO CERTIFICADO ===");
  console.log("Código:", codigo);
  
  // Usar URL absoluta para server component
  const baseUrl = process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000";
  
  try {
    const url = `${baseUrl}/api/certificado/${codigo}`;
    console.log("URL da API interna:", url);
    
    const response = await fetch(url, {
      cache: "no-store"
    });
    
    console.log("Status:", response.status);
    
    if (!response.ok) {
      const error = await response.json();
      console.error("Erro:", error);
      return null;
    }
    
    const data = await response.json();
    console.log("✅ Certificado encontrado");
    return data;
  } catch (err: any) {
    console.error("❌ Erro ao buscar certificado:", err.message);
    return null;
  }
}

export default async function CertificadoPage({
  params,
}: {
  params: { codigo: string };
}) {
  const { codigo } = await params;
  const certificado = await fetchCertificado(codigo);

  if (!certificado || certificado.revogado) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center p-4">
        <div className="bg-white rounded-lg shadow-lg p-8 text-center max-w-md">
          <h1 className="text-xl font-bold text-red-600">Certificado Inválido</h1>
          <p className="mt-2 text-gray-600">
            {certificado?.revogado
              ? "Este certificado foi revogado e não é mais válido."
              : "Certificado não encontrado."}
          </p>
          <p className="mt-2 text-sm text-gray-400">Código: {codigo}</p>
          <a href="/eventos" className="mt-4 inline-block text-indigo-600 hover:underline">
            Voltar
          </a>
        </div>
      </div>
    );
  }

  return <CertificadoView certificado={certificado} />;
}