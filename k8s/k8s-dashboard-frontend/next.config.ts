/** @type {import('next').NextConfig} */
const nextConfig = {
  // Add any specific Next.js configurations here
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: "http://localhost:5000/api/:path*",
      },
    ];
  },
};

export default nextConfig;
