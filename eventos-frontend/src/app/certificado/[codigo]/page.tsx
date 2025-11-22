import axios from "axios";
import CertificadoView from "./CertificadoView";

const CERTIFICADOS_URL = process.env.NEXT_PUBLIC_CERTIFICADOS_URL;

async function fetchCertificado(codigo: string) {
  try {
    const r = await axios.get(`${CERTIFICADOS_URL}/codigo/${codigo}`);
    return r.data;
  } catch {
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
          <a href="/eventos" className="mt-4 inline-block text-indigo-600 hover:underline">
            Voltar
          </a>
        </div>
      </div>
    );
  }

  return <CertificadoView certificado={certificado} />;
}