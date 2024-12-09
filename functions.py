import paramiko
from schemas.schemas import ConteoArchivos
from datetime import datetime
import logging
from typing import List, Tuple
import os
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
_logger = logging.getLogger(__name__)


def clear_console() -> None:
    """
    Limpia la consola en Windows, macOS y Linux.

    Returns:
        None
    """
    # Comando para Windows
    if os.name == 'nt':
        os.system('cls')
    # Comando para macOS y Linux
    else:
        os.system('clear')
    print()
    print()
    _logger.info("CONSOLA LIMPIA----------//---------------//--------------//---------------//----------------//")
    print()


import paramiko
from typing import Tuple

def cliente_sft(host: str, port: int, username: str, password: str) -> Tuple[paramiko.SFTPClient, paramiko.Transport]:
    """
    Establece una conexión SFTP y retorna el cliente y el transporte.

    Args:
        host (str): Dirección del servidor SFTP.
        port (int): Puerto del servidor SFTP.
        username (str): Nombre de usuario para el acceso SFTP.
        password (str): Contraseña para el acceso SFTP.

    Returns:
        Tuple[paramiko.SFTPClient, paramiko.Transport]: Cliente SFTP y transporte SFTP.
    """
    transport = paramiko.Transport((host, port))
    transport.connect(username=username, password=password)
    sftp = paramiko.SFTPClient.from_transport(transport)
    return sftp, transport


def read_from_sftp(host: str, port: int, username: str, password: str) -> ConteoArchivos:
    """
    Conecta a un servidor SFTP, lista los archivos y clasifica los archivos por tipo.

    Args:
        host (str): Dirección del servidor SFTP.
        port (int): Puerto del servidor SFTP.
        username (str): Nombre de usuario para el acceso SFTP.
        password (str): Contraseña para el acceso SFTP.

    Returns:
        ConteoArchivos: Objeto que contiene listas de archivos .tar.gz, .zip y .rar.
    """
    sftp, transport = cliente_sft(host, port, username, password)

    # Listar todos los archivos en el directorio remoto
    archivos = sftp.listdir()

    # Filtrar archivos con las extensiones deseadas
    archivos_tar_gz = [archivo for archivo in archivos if archivo.endswith('.tar.gz')]
    archivos_zip = [archivo for archivo in archivos if archivo.endswith('.zip')]
    archivos_rar = [archivo for archivo in archivos if archivo.endswith('.rar')]

    # Cerrar la conexión SFTP
    sftp.close()
    transport.close()
    return ConteoArchivos(tar_gz_files=archivos_tar_gz, zip_files=archivos_zip, rar_files=archivos_rar)


def fecha_mes_vencido() -> str:
    """
    Calcula y devuelve la fecha del mes anterior en formato 'YYYYMM'. 
    Returns: 
        str: Una cadena representando el mes vencido en formato 'YYYYMM'.
    """
    # Obtener el mes y año actuales
    ahora = datetime.now()
    anho_actual = ahora.year
    mes_actual = ahora.month
    
    # Calcular el mes y año del mes vencido
    mes_vencido = mes_actual - 1
    if mes_vencido == 0:
        mes_vencido = 12
        anho_vencido = anho_actual - 1
    else:
        anho_vencido = anho_actual
    fecha_vencida = str(anho_vencido)+str(mes_vencido)
    return fecha_vencida


def extraer_fecha(nombre:str) -> str:
    """
    Extrae y devuelve el año y mes desde el nombre de un archivo.
    Args: 
        nombre (str): El nombre del archivo desde el cual se extraerá la fecha. 
    Returns: 
        str: Una cadena representando el año y el mes en formato 'YYYYMM'.
    """
    fecha_str = nombre[:6]
    return fecha_str


def filtrar_facturas_mes_vencido(conteo_archivos: ConteoArchivos) -> List[str]:
    """
    Filtra los archivos correspondientes al mes vencido en la instancia de ConteoArchivos. 
    Args: 
        ConteoArchivos (ConteoArchivos): Una instancia de la clase ConteoArchivos que contiene listas de nombres de archivos. 
    Returns: 
        List[str]: Una lista de nombres de archivos que corresponden al mes vencido.
    """
    fecha_vencida = fecha_mes_vencido()

    lista_atributos_ConteoArchivos = ["tar_gz_files", "zip_files", "rar_files"]
    lista_archivos_copiar = []
    for atributo in lista_atributos_ConteoArchivos:
        archivos = getattr(conteo_archivos, atributo)
        print()
        for archivo in archivos:
            print()
            _logger.info(f"Archivo: {archivo}")
            if extraer_fecha(archivo) == fecha_vencida:
                _logger.info(f"Fecha del archivo: {extraer_fecha(archivo)}")
                _logger.info(f"Fecha del mes vencido: {fecha_vencida}")
                lista_archivos_copiar.append(archivo)
    print()
    _logger.info(f"Lista final: {lista_archivos_copiar}")
    print()
    return lista_archivos_copiar


def descargar_archivos_sftp(conteo_archivos: ConteoArchivos, host: str, port: int, username: str, password: str, lista_archivos_copiar: List[str], destino: str) -> None:
    """
    Descarga archivos desde un servidor SFTP cuyos nombres coincidan con los de una lista dada.

    Args:
        host (str): Dirección del servidor SFTP.
        port (int): Puerto del servidor SFTP.
        username (str): Nombre de usuario para el acceso SFTP.
        password (str): Contraseña para el acceso SFTP.
        archivos_a_descargar (List[str]): Lista de nombres de archivos a descargar.
        destino (str): Directorio destino donde se guardarán los archivos descargados.

    Returns:
        None
    """
    # Crear el cliente SFTP
    _logger.info("Estableciendo conexión SFTP")
    sftp, transport = cliente_sft(host, port, username, password)
    
    lista_archivos_copiar = filtrar_facturas_mes_vencido(conteo_archivos)
        
    # Descargar los archivos que coinciden con los nombres en la lista
    for archivo in lista_archivos_copiar:
        remote_file_path = Path(archivo)
        local_file_path = Path.cwd() / destino / archivo
                    
        if local_file_path.exists():
            _logger.warning(f"El archivo ya existe en el directorio de descarga, se omite dicha descarga: {local_file_path}")
            continue
        try:

            _logger.info(f"Descargando archivo: {archivo}")
            sftp.get(str(remote_file_path), str(local_file_path))
            _logger.info(f"{archivo} descargado satisfactoriamente")
        except Exception as e:
            _logger.error(f"Error descargando el archivo: {archivo}")
    
    # Cerrar la conexión SFTP
    _logger.info("Cerrando conexión SFTP")
    sftp.close()
    transport.close()
