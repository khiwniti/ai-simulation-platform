'use client'

import React, { useRef, useMemo } from 'react'
import { Canvas, useFrame, useThree } from '@react-three/fiber'
import { OrbitControls, Text, Box, Sphere, Line } from '@react-three/drei'
import * as THREE from 'three'

interface SimulationCanvasProps {
  isRunning: boolean
}

// Bridge component for 3D visualization
function BridgeStructure({ isRunning }: { isRunning: boolean }) {
  const groupRef = useRef<THREE.Group>(null)
  const bridgeRef = useRef<THREE.Mesh>(null)
  const cableRefs = useRef<THREE.Mesh[]>([])

  useFrame((state) => {
    if (!groupRef.current) return
    
    // Gentle rotation when not running
    if (!isRunning) {
      groupRef.current.rotation.y = Math.sin(state.clock.elapsedTime * 0.2) * 0.1
    }
    
    // Animate bridge construction when running
    if (isRunning && bridgeRef.current) {
      const time = state.clock.elapsedTime * 2
      bridgeRef.current.scale.x = Math.min(1, (time % 4) / 2)
      
      // Animate cable tension
      cableRefs.current.forEach((cable, index) => {
        if (cable) {
          const offset = index * 0.5
          cable.position.y = -0.5 + Math.sin(time + offset) * 0.1
        }
      })
    }
  })

  // Create bridge geometry
  const bridgeGeometry = useMemo(() => {
    const points = []
    for (let i = 0; i <= 100; i++) {
      const x = (i / 100) * 10 - 5
      const y = Math.sin((i / 100) * Math.PI) * 0.5 - 1
      points.push(new THREE.Vector3(x, y, 0))
    }
    return points
  }, [])

  return (
    <group ref={groupRef}>
      {/* Main bridge deck */}
      <Box
        ref={bridgeRef}
        args={[8, 0.2, 1]}
        position={[0, -1, 0]}
      >
        <meshStandardMaterial 
          color={isRunning ? "#4f9ef8" : "#6b7280"} 
          roughness={0.3}
        />
      </Box>

      {/* Bridge towers */}
      <Box args={[0.3, 4, 0.3]} position={[-3, 1, 0]}>
        <meshStandardMaterial color="#374151" />
      </Box>
      <Box args={[0.3, 4, 0.3]} position={[3, 1, 0]}>
        <meshStandardMaterial color="#374151" />
      </Box>

      {/* Cable stays */}
      {Array.from({ length: 6 }, (_, i) => {
        const x = (i - 2.5) * 1.2
        return (
          <Line
            key={i}
            points={[
              [x, -0.9, 0],
              [x > 0 ? 3 : -3, 3, 0]
            ]}
            color={isRunning ? "#f59e0b" : "#9ca3af"}
            lineWidth={2}
          />
        )
      })}

      {/* Support pillars in water */}
      <Box args={[0.5, 2, 0.5]} position={[0, -2, 0]}>
        <meshStandardMaterial color="#1f2937" />
      </Box>

      {/* Loading indicators when simulation is running */}
      {isRunning && (
        <>
          <Sphere args={[0.1]} position={[-4, 2, 0]}>
            <meshStandardMaterial color="#ef4444" emissive="#ef4444" emissiveIntensity={0.5} />
          </Sphere>
          <Sphere args={[0.1]} position={[4, 2, 0]}>
            <meshStandardMaterial color="#10b981" emissive="#10b981" emissiveIntensity={0.5} />
          </Sphere>
        </>
      )}

      {/* Bridge label */}
      <Text
        position={[0, 4, 0]}
        fontSize={0.5}
        color={isRunning ? "#f59e0b" : "#6b7280"}
        anchorX="center"
        anchorY="middle"
      >
        {isRunning ? "Autonomous Bridge Design in Progress..." : "150m Cable-Stayed Bridge"}
      </Text>
    </group>
  )
}

// Loading particles for simulation effect
function LoadingParticles({ isRunning }: { isRunning: boolean }) {
  const particlesRef = useRef<THREE.Points>(null)
  
  const particles = useMemo(() => {
    const positions = new Float32Array(200 * 3)
    for (let i = 0; i < 200; i++) {
      positions[i * 3] = (Math.random() - 0.5) * 20
      positions[i * 3 + 1] = (Math.random() - 0.5) * 10
      positions[i * 3 + 2] = (Math.random() - 0.5) * 10
    }
    return positions
  }, [])

  useFrame((state) => {
    if (!particlesRef.current || !isRunning) return
    
    const positions = particlesRef.current.geometry.attributes.position.array as Float32Array
    for (let i = 0; i < positions.length; i += 3) {
      positions[i + 1] += Math.sin(state.clock.elapsedTime + i) * 0.01
    }
    particlesRef.current.geometry.attributes.position.needsUpdate = true
  })

  if (!isRunning) return null

  return (
    <points ref={particlesRef}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          count={particles.length / 3}
          array={particles}
          itemSize={3}
        />
      </bufferGeometry>
      <pointsMaterial size={0.05} color="#f59e0b" transparent opacity={0.6} />
    </points>
  )
}

// Environment setup
function SceneEnvironment() {
  const { scene } = useThree()
  
  React.useEffect(() => {
    scene.background = new THREE.Color('#f0f9ff')
    scene.fog = new THREE.Fog('#f0f9ff', 10, 50)
  }, [scene])

  return (
    <>
      <ambientLight intensity={0.6} />
      <directionalLight position={[10, 10, 5]} intensity={0.8} castShadow />
      <pointLight position={[0, 5, 0]} intensity={0.4} color="#f59e0b" />
    </>
  )
}

export default function SimulationCanvas({ isRunning }: SimulationCanvasProps) {
  return (
    <div className="w-full h-full simulation-canvas">
      <Canvas
        camera={{ position: [8, 4, 8], fov: 50 }}
        shadows
      >
        <SceneEnvironment />
        <BridgeStructure isRunning={isRunning} />
        <LoadingParticles isRunning={isRunning} />
        <OrbitControls 
          enablePan={true} 
          enableZoom={true} 
          enableRotate={true}
          autoRotate={!isRunning}
          autoRotateSpeed={0.5}
        />
      </Canvas>

      {/* Overlay controls */}
      <div className="absolute top-4 left-4 bg-black/50 text-white px-3 py-1 rounded text-sm">
        {isRunning ? (
          <span className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse" />
            <span>Simulation Active</span>
          </span>
        ) : (
          <span>Mouse: Rotate • Scroll: Zoom</span>
        )}
      </div>

      {/* Performance overlay */}
      <div className="absolute bottom-4 right-4 bg-black/50 text-white px-3 py-1 rounded text-xs">
        3D Rendering: WebGL
      </div>
    </div>
  )
}