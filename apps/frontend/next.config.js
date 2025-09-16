/** @type {import('next').NextConfig} */
const nextConfig = {
  transpilePackages: ['@ai-jupyter/shared'],
  typescript: {
    // !! WARN !!
    // Dangerously allow production builds to successfully complete even if
    // your project has type errors.
    // !! WARN !!
    ignoreBuildErrors: true,
  },
  eslint: {
    // Warning: This allows production builds to successfully complete even if
    // your project has ESLint errors.
    ignoreDuringBuilds: true,
  },
  webpack: (config) => {
    // Handle Three.js
    config.externals = config.externals || [];
    config.externals.push({
      'three/examples/jsm/loaders/GLTFLoader': 'THREE.GLTFLoader',
    });
    
    return config;
  },
};

module.exports = nextConfig;