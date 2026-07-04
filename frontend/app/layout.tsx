import type { Metadata } from "next";
import { Barlow_Condensed } from "next/font/google";
import "./globals.css";
import NavBar from "@/components/NavBar";
import Footer from "@/components/Footer";
import { Analytics } from "@vercel/analytics/next";
import { SpeedInsights } from "@vercel/speed-insights/next";

const barlow = Barlow_Condensed({
  subsets: ["latin"],
  weight: ["700", "800", "900"],
  variable: "--font-barlow",
});

export const metadata: Metadata = {
  title: "PunchNotes — Comedy Analytics",
  description: "Structured analysis of stand-up comedy. Explore Kill Tony sets, comedians, and jokes broken down by premise, mechanism, and audience response.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://api.punchnotes.app" crossOrigin="anonymous" />
        <link rel="preconnect" href="https://img.youtube.com" crossOrigin="anonymous" />
      </head>
      <body suppressHydrationWarning className={barlow.variable}>
        <div className="min-h-screen flex flex-col">
          <NavBar />
          <main className="flex-grow">{children}</main>
          <Footer />
        </div>
        <Analytics />
        <SpeedInsights />
      </body>
    </html>
  );
}
