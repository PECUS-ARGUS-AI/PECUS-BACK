"use client";

import { Canvas } from "@react-three/fiber";
import { OrbitControls } from "@react-three/drei";
import { useLoader } from "@react-three/fiber";
import * as THREE from "three";

export default function Depth3D({ imageUrl }: { imageUrl: string }) {
    const tex = useLoader(THREE.TextureLoader, imageUrl);

    return (
        <div className="w-full h-[400px] rounded-xl overflow-hidden border border-white/20 shadow-lg">
            <Canvas camera={{ position: [0, 0, 2] }}>
                <ambientLight />
                <mesh>
                    <planeGeometry args={[2, 1.3, 200, 200]} />
                    <meshStandardMaterial
                        displacementMap={tex}
                        displacementScale={0.4}
                        map={tex}
                    />
                </mesh>
                <OrbitControls />
            </Canvas>
        </div>
    );
}
