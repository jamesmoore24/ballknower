import "./globals.css";
import type { Metadata } from "next";
import { Inter } from "next/font/google";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "BallKnower",
  description: "An open-source AI agent for sports analysis",
  openGraph: {
    title: "BallKnower - Sports Betting",
    description: "An open-source AI agent for sports analysis",
    url: "https://ballknower.bet",
    type: "website",
    images: [
      {
        url: "https://ballknower.bet/images/logo.png",
        width: 1200,
        height: 630,
        alt: "BallKnower Logo",
      },
    ],
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
