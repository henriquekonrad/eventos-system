import { fetchEventosServer } from "@/lib/api";

export default async function EventosPage() {
  const eventos: any[] = await fetchEventosServer();

  return (
    <main style={{ maxWidth: 900, margin: "2rem auto" }}>
      <h1>Eventos</h1>
      <ul>
        {eventos.map(ev => (
          <li key={ev.id}>
            <a href={`/app/eventos/${ev.id}`}>
              {ev.titulo} — {new Date(ev.inicio_em).toLocaleString()}
            </a>
          </li>
        ))}
      </ul>
    </main>
  );
}
