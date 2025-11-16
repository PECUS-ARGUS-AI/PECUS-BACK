"use client";

import { useState } from "react";
import UploadCard from "./components/UploadCard";
import MetricAnimated from "./components/MetricAnimated";
import Depth3D from "./components/Depth3D";
import ThemeToggle from "./components/ThemeToggle";

export default function Home() {
    const [loading, setLoading] = useState(false);
    const [resultado, setResultado] = useState<any | null>(null);
    const [preview, setPreview] = useState<string | null>(null);

    const [contorno, setContorno] = useState<string | null>(null);
    const [depth, setDepth] = useState<string | null>(null);

    const handleUpload = async (file: File) => {
        setPreview(URL.createObjectURL(file));
        setLoading(true);
        setResultado(null);

        const formData = new FormData();
        formData.append("file", file);

        try {
            const resp = await fetch("http://127.0.0.1:8000/estimar", {
                method: "POST",
                body: formData
            });

            if (!resp.ok) throw new Error("Erro ao enviar imagem");

            const json = await resp.json();
            setResultado(json.resultado);

            setContorno("http://127.0.0.1:8000/saida/bovino_contorno.png");
            setDepth("http://127.0.0.1:8000/saida/resultado_profundidade.png");

        } catch (err) {
            alert("Erro ao processar imagem");
        }

        setLoading(false);
    };

    return (
        <main className="min-h-screen flex flex-col items-center p-6">


            <ThemeToggle />

            <h1 className="text-5xl font-bold mt-10 text-center">
                🐂 PECUS — Pesagem por Imagem
            </h1>

            <p className="text-lg opacity-80 mt-2 text-center">
                IA para análise volumétrica de bovinos
            </p>

            {!resultado && !loading && (
                <div className="mt-10 w-full max-w-xl">
                    <UploadCard onFileSelect={handleUpload} />

                    {preview && (
                        <img
                            src={preview}
                            className="mt-6 rounded-2xl shadow-xl w-full"
                        />
                    )}
                </div>
            )}

            {loading && (
                <p className="mt-10 animate-pulse text-xl">Processando imagem...</p>
            )}

            {resultado && (
                <div className="mt-10 w-full max-w-4xl">

                    <h2 className="text-2xl font-bold mb-2">📥 Imagem Enviada</h2>
                    <img src={preview!} className="rounded-2xl shadow-xl mb-8" />

                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-10">
                        <div>
                            <h2 className="text-xl font-bold mb-2">📤 Contorno</h2>
                            <img src={contorno!} className="rounded-xl shadow-lg" />
                        </div>
                        <div>
                            <h2 className="text-xl font-bold mb-2">🌈 Mapa de Profundidade</h2>
                            <img src={depth!} className="rounded-xl shadow-lg" />
                        </div>
                    </div>

                    <h2 className="text-2xl font-bold mt-4 mb-4">🧠 Visualização 3D da Profundidade</h2>
                    <Depth3D imageUrl={depth!} />

                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-10">
                        <MetricAnimated label="Comprimento" value={resultado.comprimento} />
                        <MetricAnimated label="Largura média" value={resultado.largura_media} />
                        <MetricAnimated label="Altura média" value={resultado.altura_media} />
                        <MetricAnimated label="Volume (m³)" value={resultado.volume_m3} />
                    </div>

                    <div className="text-center text-3xl mt-8 font-bold">
                        Peso estimado: 
                        <span className="text-green-500 dark:text-green-400 ml-2">
                            {resultado.massa_kg} kg
                        </span>
                    </div>
                </div>
            )}
        </main>
    );
}