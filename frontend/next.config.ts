import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Prevent Next.js from redirecting trailing-slash URLs to their non-slash
  // equivalents — without this, Django's APPEND_SLASH causes redirect loops.
  skipTrailingSlashRedirect: true,

  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "api.jokescore.com",
        pathname: "/media/**",
      },
      {
        protocol: "http",
        hostname: "localhost",
        port: "8000",
        pathname: "/media/**",
      },
      {
        protocol: "https",
        hostname: "img.youtube.com",
        pathname: "/vi/**",
      },
    ],
    minimumCacheTTL: 60 * 60 * 24 * 31,
  },

  async headers() {
    return [
      {
        source: "/:path*",
        headers: [
          { key: "X-Frame-Options", value: "DENY" },
          { key: "X-Content-Type-Options", value: "nosniff" },
          { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
          { key: "Permissions-Policy", value: "camera=(), microphone=(), geolocation=()" },
        ],
      },
    ];
  },

  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${process.env.DJANGO_API_URL ?? "http://localhost:8000"}/api/:path*/`,
      },
    ];
  },
};

export default nextConfig;
