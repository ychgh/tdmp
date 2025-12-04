import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Test Data Management Platform",
  description: "AI Agent Chat Tool with RAG capabilities",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="font-sans antialiased">
        {children}
      </body>
    </html>
  );
}
