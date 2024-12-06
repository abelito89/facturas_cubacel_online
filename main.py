import uvicorn
from fastapi import FastAPI
import os
from dotenv import load_dotenv
from functions import read_from_sftp
import logging


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
_logger = logging.getLogger(__name__)

app = FastAPI()

load_dotenv()


host = os.getenv("IP_FTP")
port = os.getenv("PORT")
username = os.getenv("USER")
password = os.getenv("PASSWORD")

@app.get("/decompactar_facturas")
async def descompactar_facturas(host:str = host, port: int = int(port), username:str = username, password:str = password) -> None:
    tar_gz_files, zip_files, rar_files = read_from_sftp(host, port, username, password)
    _logger.info(f"Archivos .tar.gz: {tar_gz_files}") 
    _logger.info(f"Archivos .zip: {zip_files}") 
    _logger.info(f"Archivos .rar: {rar_files}")



if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)