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
from email_sender import send_email
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
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
    # Envio de correo de notificacion
    to_email = os.getenv("TO_EMAIL")
    subject = "Prueba"
    body = "prueba"
    send_email(to_email, subject, body)
    print()
    

def descomprimir_zip(file_path: Path, output_dir: Path) -> None:
    """
    Descomprime un archivo zip y verifica si ya está descomprimido.

    Args:
        file_path (Path): Ruta del archivo zip.
        output_dir (Path): Directorio de salida.

    Returns:
        None
    """
    try:
        with zipfile.ZipFile(file_path, 'r') as zip_ref:
            # Verificar si todos los archivos ya están descomprimidos
            all_files_exist = all((output_dir / member).exists() for member in zip_ref.namelist())
            if all_files_exist:
                _logger.info(f"El archivo ZIP: {file_path} ya está descomprimido")
                return  # Salir sin extraer nada

            # Extraer los archivos si no están descomprimidos
            _logger.info(f"Descomprimiendo archivo ZIP: {file_path}")
            zip_ref.extractall(str(output_dir))
        _logger.info(f"Archivo ZIP descomprimido: {file_path}")
    except Exception as e:
        _logger.error(f"Error al descomprimir el archivo ZIP {file_path}: {e}")


def descomprimir_rar(file_path: Path, output_dir: Path) -> None:
    """
    Descomprime un archivo rar y verifica si ya está descomprimido.

    Args:
        file_path (Path): Ruta del archivo rar.
        output_dir (Path): Directorio de salida.

    Returns:
        None
    """
    try:
        with rarfile.RarFile(file_path, 'r') as rar_ref:
            # Verificar si todos los archivos ya están descomprimidos
            all_files_exist = all((output_dir / member).exists() for member in rar_ref.getnames())
            if all_files_exist:
                _logger.info(f"El archivo RAR: {file_path} ya está descomprimido")
                return  # Salir sin extraer nada

            # Extraer los archivos si no están descomprimidos
            _logger.info(f"Descomprimiendo archivo RAR: {file_path}")
            rar_ref.extractall(output_dir)
        _logger.info(f"Archivo RAR descomprimido: {file_path}")
    except Exception as e:
        _logger.error(f"Error al descomprimir el archivo RAR {file_path}: {e}")



def descomprimir_tar_gz(file_path: Path, output_dir: Path) -> None:
    """
    Descomprime un archivo tar.gz y verifica si ya está descomprimido.

    Args:
        file_path (Path): Ruta del archivo tar.gz.
        output_dir (Path): Directorio de salida.

    Returns:
        None
    """
    try:
        with tarfile.open(file_path, 'r:gz') as tar_ref:
            # Verificar si todos los archivos ya están descomprimidos
            all_files_exist = all((output_dir / member).exists() for member in tar_ref.getnames())
            if all_files_exist:
                _logger.info(f"El archivo TAR.GZ: {file_path} ya está descomprimido")
                return  # Salir sin extraer nada

            # Extraer los archivos si no están descomprimidos
            _logger.info(f"Descomprimiendo archivo TAR.GZ: {file_path}")
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
    _logger.info(f"Iniciando descompresión")

    # Verificar que el directorio existe
    if not dir_path.exists() or not dir_path.is_dir():
        raise FileNotFoundError(f"El directorio {directorio} no existe o no es un directorio válido")

    # Recorrer todos los archivos en el directorio
    for file_path in dir_path.iterdir():
        if file_path.suffix in ['.zip', '.rar'] or file_path.name.endswith('.tar.gz'):
            # Tomar los primeros 6 caracteres del nombre del archivo
            output_dir_name = file_path.name[:6]
            output_dir = dir_path / output_dir_name

            # Crear el directorio de salida si no existe
            output_dir.mkdir(parents=True, exist_ok=True)

            # Llamar a la función adecuada para descomprimir
            if file_path.suffix == '.zip':
                descomprimir_zip(file_path, output_dir)  # Usar output_dir
            elif file_path.suffix == '.rar':
                descomprimir_rar(file_path, output_dir)  # Usar output_dir
            elif file_path.name.endswith('.tar.gz') or file_path.suffix in ['.tar.gz', '.tgz']:
                descomprimir_tar_gz(file_path, output_dir)  # Usar output_dir
        else:
            _logger.warning(f"Tipo de archivo no soportado: {file_path}")
            

def eliminar_comprimidos(directorio: str) -> None:
    """
    Elimina archivos comprimidos (.zip, .rar, .tar.gz) en el directorio dado.
    
    Args: 
        directorio (str): Ruta del directorio donde se encuentran los archivos comprimidos.
         
    Returns:
        None
        
    Raises: 
        FileNotFoundError: Si el directorio no existe o no es válido.
    """
    dir_path = Path(directorio)
    _logger.info(f"Iniciando deliminación de descomprimidos")

    # Verificar que el directorio existe
    if not dir_path.exists() or not dir_path.is_dir():
        raise FileNotFoundError(f"El directorio {directorio} no existe o no es un directorio válido")

    # Recorrer todos los archivos en el directorio
    for file_path in dir_path.iterdir():
        if file_path.suffix in ['.zip', '.rar'] or file_path.name.endswith('.tar.gz'):
            try:
                os.remove(file_path)
                _logger.info(f"Archivo {file_path} eliminado")
            except Exception as e:
                _logger.error(f"No se puedo eliminar el archivo: {e}")


def subir_carpeta_a_sftp(host: str, port: int, username: str, password: str, carpeta_local: str, carpeta_buscar: str) -> None:
    """
    Busca una carpeta específica en el directorio local y sube su contenido a un servidor SFTP.

    Args:
        host (str): Dirección del servidor SFTP.
        port (int): Puerto del servidor SFTP.
        username (str): Nombre de usuario para el acceso SFTP.
        password (str): Contraseña para el acceso SFTP.
        carpeta_local (str): Ruta del directorio local donde se buscará la carpeta.
        carpeta_buscar (str): Nombre de la carpeta a buscar y subir.
    """
    sftp, transport = cliente_sft(host, port, username, password)
    
    carpeta_local_path = Path(carpeta_local)
    
    def buscar_carpeta(carpeta_local_path: Path, carpeta_buscar: str):
        """
        Busca una carpeta específica dentro de un directorio dado.

        Args:
            carpeta_local_path (Path): Ruta del directorio local donde buscar la carpeta.
            carpeta_buscar (str): Nombre de la carpeta a buscar.

        Returns:
            Path or None: Retorna la ruta de la carpeta encontrada o None si no se encuentra.
        """
        _logger.debug(f"Buscando carpeta {carpeta_buscar} en {carpeta_local_path}")
        for item in carpeta_local_path.iterdir():
            _logger.debug(f"Encontrado: {item}")
            if item.is_dir() and item.name == carpeta_buscar:
                _logger.debug(f"Carpeta encontrada: {item}")
                return item
        return None
    
    carpeta_encontrada = buscar_carpeta(carpeta_local_path, carpeta_buscar)
    _logger.info(f"Ya está creada la carpeta {carpeta_encontrada}")
    _logger.info(f"Tipo de carpeta_encontrada: {type(carpeta_encontrada)}")
    _logger.info(f"Valor de carpeta_encontrada: {carpeta_encontrada}")

    
    if carpeta_encontrada:
        _logger.info(f"Entrando en el IF")
        try:
            # Obtén la ruta de inicio del usuario
            home_directory = sftp.normalize(".")
            _logger.info(f"La ruta de inicio del usuario SFTP es: {home_directory}")
            
            # Ajusta la ruta remota
            remote_directory_path = f"{home_directory.rstrip('/')}/{carpeta_encontrada.name}"
            _logger.info(f"Ruta remota ajustada correctamente: {remote_directory_path}")

            try:
                # Ajustar manualmente la ruta base a /upload
                home_directory = '/upload'  # Directorio base en el contenedor Docker
                _logger.info(f"Directorio base manual ajustado a: {home_directory}")

                # Ajustar la ruta remota
                remote_directory_path = f"{home_directory.rstrip('/')}/{carpeta_encontrada.name}"
                _logger.info(f"Ruta remota ajustada correctamente: {remote_directory_path}")

                # Verificar si el directorio remoto existe
                _logger.info(f"Verificando si el directorio remoto {remote_directory_path} existe.")
                sftp.stat(remote_directory_path)
                _logger.info(f"Directorio remoto {remote_directory_path} ya existe.")
            except FileNotFoundError:
                # Si no existe, intenta crearlo
                _logger.info(f"Directorio remoto {remote_directory_path} no existe. Intentando crearlo...")
                try:
                    sftp.mkdir(remote_directory_path)
                    _logger.info(f"Directorio remoto creado exitosamente: {remote_directory_path}")
                except Exception as e:
                    _logger.error(f"Error creando directorio remoto {remote_directory_path}: {e}")
                    raise

            except IOError as e:
                # Maneja cualquier otro error de entrada/salida
                _logger.error(f"Error al verificar o crear el directorio remoto {remote_directory_path}: {e}")
                raise
            except Exception as e:
                # Maneja errores inesperados
                _logger.error(f"Error inesperado al manejar el directorio remoto {remote_directory_path}: {e}")
                raise

            
            # Iterar sobre todos los archivos PDF en la carpeta encontrada
            for pdf_file in carpeta_encontrada.glob('*.pdf'):
                remote_file_path = f"{remote_directory_path}/{pdf_file.name}"
                
                # Debugging: Verificar permisos locales y remotos antes de subir 
                local_permissions = os.access(pdf_file, os.R_OK) 
                remote_permissions = sftp.stat(remote_directory_path).st_mode 
                
                sftp.stat(remote_directory_path).st_mode 
                _logger.info(f"Permisos locales para {pdf_file}: {local_permissions}") 
                _logger.info(f"Permisos del directorio remoto {remote_directory_path}: {remote_permissions}")
                
                # Subir el archivo PDF al SFTP
                _logger.info(f"Subiendo {pdf_file} a {remote_file_path}")
                sftp.put(str(pdf_file), remote_file_path)
                _logger.info(f"Archivo {pdf_file} subido a {remote_file_path}")
            
            sftp.close()
            transport.close()
            _logger.info("Carpeta subida exitosamente")
        except IOError as e:
            _logger.error(f"Error al subir la carpeta: {e}")
        except Exception as e:
            _logger.error(f"Error inesperado al subir la carpeta: {e}")
    else:
        _logger.warning(f"No se encontró la carpeta {carpeta_buscar} en la carpeta {carpeta_local}")
        sftp.close()
        transport.close()
