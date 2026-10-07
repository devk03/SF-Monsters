import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "SF Mini Monsters — The Fog Signal",
  description: "Play an original San Francisco mini-monster adventure in your browser, or download the GBA ROM.",
  other: {
    "codex-preview": "development",
  },
  icons: {
    icon: "/favicon.svg",
    shortcut: "/favicon.svg",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">{children}</body>
    </html>
  );
}
