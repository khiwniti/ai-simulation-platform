/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    transpilePackages: ['@ai-jupyter/shared'],
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