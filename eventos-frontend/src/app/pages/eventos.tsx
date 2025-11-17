// pages/app/eventos/index.tsx
import { GetServerSideProps } from "next";
import { fetchEventosServer } from "../../../lib/api";

export default function EventosPage({ eventos }: { eventos: any[] }) {
  return (
    <main style={{maxWidth:900, margin:"2rem auto"}}>
      <h1>Eventos</h1>
      <ul>
        {eventos.map(ev => (
          <li key={ev.id}>
            <a href={`/app/eventos/${ev.id}`}>{ev.titulo} — {new Date(ev.inicio_em).toLocaleString()}</a>
          </li>
        ))}
      </ul>
    </main>
  );
}

export const getServerSideProps: GetServerSideProps = async (ctx) => {
  try {
    const eventos = await fetchEventosServer(ctx.req);
    return { props: { eventos } };
  } catch (e) {
    return { props: { eventos: [] } };
  }
};
