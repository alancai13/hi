import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Allow importing from packages/shared
  transpilePackages: [],

  // TODO: Add image domains when screenshots/previews are added
  // images: { remotePatterns: [] },
};

export default nextConfig;
