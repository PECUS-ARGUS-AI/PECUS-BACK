from fastapi import FastAPI, File, UploadFile
import numpy as np
import cv2
from processamento.estimativa import processar_bovino
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="API de Pesagem de Gado por Imagem")

app.mount("/static", StaticFiles(directory="saida"), name="static")

origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://192.168.0.0/16"  # permite rede local inteira
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/estimar")
async def estimar_gado(file: UploadFile = File(...)):
    conteudo = await file.read()

    resultado = processar_bovino(conteudo)

    return {"resultado": resultado}



app.mount("/saida", StaticFiles(directory="saida"), name="saida")
