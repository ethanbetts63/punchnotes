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
  icons: {
    icon: [
      { url: '/punchnotes_logo_48x48.png', sizes: '48x48', type: 'image/png' },
      { url: '/punchnotes_logo_96x96.png', sizes: '96x96', type: 'image/png' },
      { url: '/punchnotes_logo_192x192.png', sizes: '192x192', type: 'image/png' },
    ],
    apple: [
      { url: '/punchnotes_logo_180x180.png', sizes: '180x180', type: 'image/png' },
    ],
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://api.punchnotes.app" />
        <link rel="dns-prefetch" href="https://api.punchnotes.app" />
        <link rel="preconnect" href="https://img.youtube.com" />
        <link rel="dns-prefetch" href="https://img.youtube.com" />
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
