import uvicorn
from fastapi import FastAPI
import os
from dotenv import load_dotenv
from functions import ejecutar_descompactar_facturas

app = FastAPI()

load_dotenv()

host = os.getenv("IP_FTP")
port = os.getenv("PORT")
username = os.getenv("USER")
password = os.getenv("PASSWORD")

if not all([host, port, username, password]):
    raise ValueError("Faltan variables críticas en el archivo .env (IP_FTP, PORT, USER, PASSWORD).")

# Validación adicional para `PORT`
try:
    port = int(port)  # Asegura que sea un número
except ValueError:
    raise ValueError("El puerto (PORT) debe ser un número válido.")

@app.get("/descompactar_facturas")
async def descompactar_facturas(host:str = host, port: int = int(port), username:str = username, password:str = password) -> None:
    ejecutar_descompactar_facturas(host, port, username, password)

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)