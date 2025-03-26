import "./globals.css";
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import Icon from "@/public/icon.png";
import Icon16 from "@/public/icon16.png";
import Icon32 from "@/public/icon32.png";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "BallKnower",
  description: "An open-source AI agent for sports analysis",
  icons: {
    icon: [
      { url: Icon.src },
      { url: Icon16.src, sizes: "16x16", type: "image/png" },
      { url: Icon32.src, sizes: "32x32", type: "image/png" },
    ],
    apple: [{ url: "/apple-touch-icon.png" }],
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={inter.className}>{children}</body>
    </html>
  );
}
