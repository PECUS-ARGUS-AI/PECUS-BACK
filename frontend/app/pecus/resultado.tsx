"use client";

export default function Resultado({ resultado, imagemEnviada }) {
  return (
    <div className="mx-auto max-w-5xl mt-10">
      <h2 className="text-3xl font-bold mb-6 text-center">Resultado da Estimativa</h2>

      {/* Imagem enviada */}
      {imagemEnviada && (
        <div className="mb-10">
          <h3 className="text-xl font-semibold mb-2">Imagem enviada</h3>
          <img
            src={imagemEnviada}
            className="rounded-xl shadow-md w-full"
            alt="Imagem enviada"
          />
        </div>
      )}

      {/* Métricas */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-12">
        <Metric label="Comprimento (m)" value={resultado.comprimento.toFixed(2)} />
        <Metric label="Largura média (m)" value={resultado.largura_media.toFixed(2)} />
        <Metric label="Altura média (m)" value={resultado.altura_media.toFixed(2)} />
        <Metric label="Volume (m³)" value={resultado.volume_m3.toFixed(4)} />
      </div>

      <div className="mb-12">
        <Metric
          label="Estimativa de Peso (kg)"
          value={resultado.massa_kg.toFixed(2)}
          big
        />
      </div>

      {/* Imagens geradas */}
      <h3 className="text-2xl font-semibold mb-4">📸 Imagens geradas</h3>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <ImageBox src="http://127.0.0.1:8000/static/bovino_contorno.png" label="Bovino com contorno" />
        <ImageBox src="http://127.0.0.1:8000/static/resultado_profundidade.png" label="Mapa de profundidade" />
      </div>
    </div>
  );
}

function Metric({ label, value, big = false }) {
  return (
    <div className="p-5 bg-white rounded-xl shadow border text-center">
      <p className="text-gray-500">{label}</p>
      <p className={`font-bold ${big ? "text-4xl text-blue-700" : "text-2xl"}`}>{value}</p>
    </div>
  );
}

function ImageBox({ src, label }) {
  return (
    <div>
      <p className="font-medium mb-2">{label}</p>
      <img
        src={src}
        className="rounded-xl shadow-md w-full border"
        alt={label}
      />
    </div>
  );
}
