import "./globals.css";

export const metadata = {
  title: "Eventos",
  description: "Sistema de eventos",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-BR">
      <body>{children}</body>
    </html>
  );
}
