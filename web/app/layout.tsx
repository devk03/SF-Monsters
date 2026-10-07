import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "SF Mini Monsters — The Fog Signal",
  description: "Load your Emerald ROM and apply the SF Mini Monsters patch locally. Play in the browser or download your patched GBA cartridge.",
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
