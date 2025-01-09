import requests
from typing import List, Optional
import logging
from pathlib import Path

# Configuracion del nivel de logging y de generacion del archivo .log
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
_logger = logging.getLogger(__name__)

# Paso 1: Autenticación para obtener el token
def obtener_token_servidor_sms(auth_url:str,username:str,password:str) -> Optional[str]:
    auth_data = {"username": username, "password": password}
        
    try:
        response = requests.post(auth_url, json=auth_data, verify=False, proxies=proxies)
        response.raise_for_status()
        token = response.json()["token"]  # Token obtenido
        _logger.info(f"Token obtenido por parte del servidor sms")
        return token
    except requests.RequestException as e:
        _logger.error(f"Fallo en la obtencion del token {e}")
        return None

# Paso 2: Usar el token para enviar SMS
def envio_sms(sms_url:str, token:str, mensaje_sms:str, destinos: List[str]) -> None:

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    for destino in destinos:
        sms_data = {
            "channel": "SMS",
            "sms": {
                "destination": destino,
                "message": mensaje_sms,
                "sender": "Medin"
            }
        }
        try:
            sms_response = requests.post(sms_url, json=sms_data, headers=headers, verify=False, proxies=proxies)
            if sms_response.status_code == 200:
                print(f"SMS enviado a {destino}: {sms_response.json()}")
            else:
                print(f"Error enviando SMS a {destino}: {sms_response.status_code}")
        except Exception as e:
            _logger.error(f"Fallo de envio del sms")