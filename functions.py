import paramiko
from schemas.schemas import ConteoArchivos
from datetime import datetime
import logging
from typing import List, Tuple
import os
from pathlib import Path
import zipfile
import rarfile
import tarfile

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
    

def descomprimir_zip(file_path: Path, output_dir: Path) -> None:
    """
    Descomprime un archivo zip.

    Args:
        file_path (Path): Ruta del archivo zip.
        output_dir (Path): Directorio de salida.

    Returns:
        None
    """
    try:
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            zip_ref.extractall(output_dir)
        _logger.info(f"Archivo ZIP descomprimido: {file_path}")
    except Exception as e:
        _logger.error(f"Error al descomprimir el archivo ZIP {file_path}: {e}")

def descomprimir_rar(file_path: Path, output_dir: Path) -> None:
    """
    Descomprime un archivo rar.

    Args:
        file_path (Path): Ruta del archivo rar.
        output_dir (Path): Directorio de salida.

    Returns:
        None
    """
    try:
        with rarfile.RarFile(file_path, 'r') as rar_ref:
            rar_ref.extractall(output_dir)
        _logger.info(f"Archivo RAR descomprimido: {file_path}")
    except Exception as e:
        _logger.error(f"Error al descomprimir el archivo RAR {file_path}: {e}")

def descomprimir_tar_gz(file_path: Path, output_dir: Path) -> None:
    """
    Descomprime un archivo tar.gz.

    Args:
        file_path (Path): Ruta del archivo tar.gz.
        output_dir (Path): Directorio de salida.

    Returns:
        None
    """
    try:
        with tarfile.open(file_path, 'r:gz') as tar_ref:
            tar_ref.extractall(output_dir)
        _logger.info(f"Archivo TAR.GZ descomprimido: {file_path}")
    except Exception as e:
        _logger.error(f"Error al descomprimir el archivo TAR.GZ {file_path}: {e}")
            


def descomprimir_archivos(directorio: str) -> None:
    """
    Descomprime todos los archivos .zip, .rar y .tar.gz en el directorio dado.

    Args:
        directorio (str): Ruta del directorio donde se encuentran los archivos comprimidos.

    Returns:
        None
    """
    dir_path = Path(directorio)
    _logger.info(f"Iniciando descompresion")
    # Verificar que el directorio existe
    if not dir_path.exists() or not dir_path.is_dir():
        raise FileNotFoundError(f"El directorio {directorio} no existe o no es un directorio válido")

    # Recorrer todos los archivos en el directorio
    for file_path in dir_path.iterdir(): 
        if file_path.suffix in ['.zip', '.rar'] or file_path.name.endswith('.tar.gz'): 
            output_dir = dir_path / file_path.stem # Crear una carpeta con el mismo nombre del archivo (sin la extensión) 
            output_dir.mkdir(parents=True, exist_ok=True)
            if file_path.suffix == '.zip':
                _logger.info(f"Descomprimiendo archivo ZIP: {file_path}")
                descomprimir_zip(file_path, dir_path)
            elif file_path.suffix == '.rar':
                _logger.info(f"Descomprimiendo archivo RAR: {file_path}")
                descomprimir_rar(file_path, dir_path)
            elif file_path.name.endswith('.tar.gz') or file_path.suffix in ['.tar.gz', '.tgz']:
                _logger.info(f"Descomprimiendo archivo TAR.GZ: {file_path}")
                descomprimir_tar_gz(file_path, dir_path)
        else:
            _logger.warning(f"Tipo de archivo no soportado: {file_path}")