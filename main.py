import uvicorn
from fastapi import FastAPI
import os
from dotenv import load_dotenv
from functions import read_from_sftp, filtrar_facturas_mes_vencido, clear_console, descargar_archivos_sftp, descomprimir_archivos, eliminar_comprimidos, subir_carpeta_a_sftp
import logging
from pathlib import Path


logging.basicConfig(level=logging.debug, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
_logger = logging.getLogger(__name__)

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

@app.get("/decompactar_facturas")
async def descompactar_facturas(host:str = host, port: int = int(port), username:str = username, password:str = password) -> None:
    clear_console()
    conteo_archivos = read_from_sftp(host, port, username, password)
    print()
    _logger.info(f"Archivos .tar.gz: {conteo_archivos.tar_gz_files}") 
    _logger.info(f"Archivos .zip: {conteo_archivos.zip_files}") 
    _logger.info(f"Archivos .rar: {conteo_archivos.rar_files}")
    
    lista_archivos_copiar = filtrar_facturas_mes_vencido(conteo_archivos)
    destino_descarga = "archivos_descargados"
    direccion_destino_descarga = Path.cwd() / destino_descarga
    direccion_destino_descarga.mkdir(parents=True, exist_ok=True)
    descargar_archivos_sftp(conteo_archivos, host, port, username, password, lista_archivos_copiar, direccion_destino_descarga)
    descomprimir_archivos(direccion_destino_descarga)
    carpeta_buscar = "prueba"
    subir_carpeta_a_sftp(host, port, username, password, destino_descarga, carpeta_buscar) 
    # eliminar_comprimidos(direccion_destino_descarga)


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)