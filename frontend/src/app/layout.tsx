import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Multi-Provider Twitter SSE Generator",
  description: "Realtime SSE demo with FastAPI, Next.js, Gemini, Groq, Ollama, DSPy, and GEPA.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
