import os
from dotenv import load_dotenv
from functions import ejecutar_descompactar_facturas

load_dotenv()

host = os.getenv("IP_FTP")
port = os.getenv("PORT")
username_sftp = os.getenv("USER_SFTP")
password = os.getenv("PASSWORD")

ejecutar_descompactar_facturas(host, int(port), username_sftp, password)