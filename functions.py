import paramiko
from schemas.schemas import ConteoArchivos
from datetime import datetime
import logging
from typing import List
import os

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



def read_from_sftp(host, port, username, password):
    """
        Lee archivos desde un servidor SFTP y cuenta los archivos específicos.

    Args:
        host (str): Dirección IP o nombre del host SFTP.
        port (int): Puerto del servidor SFTP.
        username (str): Nombre de usuario para conectar al servidor SFTP.
        password (str): Contraseña para conectar al servidor SFTP.

    Returns:
        ConteoArchivos: Objeto conteniendo las listas de archivos .tar.gz, .zip y .rar encontrados.

    Notes:
        - Este método conecta a un servidor SFTP usando Paramiko.
        - Lista todos los archivos en el directorio remoto.
        - Filtra y cuenta los archivos con las extensiones .tar.gz, .zip y .rar.
        - Cierra automáticamente la conexión SFTP después de completar la operación.
    """
    # Crear el cliente SFTP
    transport = paramiko.Transport((host, port))
    transport.connect(username=username, password=password)
    
    sftp = paramiko.SFTPClient.from_transport(transport)

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

# Función para extraer año y mes de un nombre de archivo
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
