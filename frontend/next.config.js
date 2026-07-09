/** @type {import('next').NextConfig} */
const path = require('path');

// Use empty string for local dev (NEXT_PUBLIC_BASE_PATH=""), otherwise default to production path
const basePath = process.env.NEXT_PUBLIC_BASE_PATH !== undefined
  ? process.env.NEXT_PUBLIC_BASE_PATH
  : "/us/nj-ctc-increase";

const nextConfig = {
  ...(basePath ? { basePath } : {}),
  output: "standalone",
  // Set the output file tracing root to this project's frontend directory
  // to avoid issues with lockfiles in parent directories
  outputFileTracingRoot: path.join(__dirname),
  async redirects() {
    // Keep pre-rename deep links working: the dashboard used to live
    // under /us/nj-ctc-eitc-expansion (basePath: false matches the raw
    // path, outside the current basePath).
    return [
      {
        source: "/us/nj-ctc-eitc-expansion/:path*",
        destination: `${basePath || "/us/nj-ctc-increase"}/:path*`,
        basePath: false,
        permanent: true,
      },
      {
        source: "/us/nj-ctc-eitc-expansion",
        destination: basePath || "/us/nj-ctc-increase",
        basePath: false,
        permanent: true,
      },
    ];
  },
};

module.exports = nextConfig;
