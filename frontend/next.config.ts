import type { NextConfig } from "next";

const PRODUCTION_API = "https://leadgen-api-bdl9.onrender.com";

const apiProxyTarget =
  process.env.API_PROXY_TARGET ??
  (process.env.VERCEL ? process.env.API_INTERNAL_URL ?? PRODUCTION_API : "http://localhost:8001");

const nextConfig: NextConfig = {
  /* config options here */
  cacheComponents: false,
  turbopack: {
    rules: {
      "*.css": {
        loaders: ["@tailwindcss/turbopack"],
        as: "*.css",
      },
    },
  },
  async rewrites() {
    return [
      {
        source: "/api/v1/:path*",
        destination: `${apiProxyTarget}/api/v1/:path*`,
      },
    ];
  },
};

export default nextConfig;
