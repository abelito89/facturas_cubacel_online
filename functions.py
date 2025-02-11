import paramiko
from schemas.schemas import ConteoArchivos
from datetime import datetime
from typing import List, Tuple
import os
from pathlib import Path
import zipfile
import rarfile
import tarfile
from dotenv import load_dotenv
from sms import obtener_token_servidor_sms, envio_sms
from log_configuration import configurar_logging, configurar_separador

load_dotenv()


def fecha_mes_borrar() -> str:
    """
    Calcula y devuelve la fecha de hace 6 meses en formato 'YYYYMM'. 
    Returns: 
        str: Una cadena representando 6 meses atras en formato 'YYYYMM'.
    """
    # Obtener el mes y año actuales
    ahora = datetime.now()
    anho_actual = ahora.year
    mes_actual = ahora.month
    
    # Calcular el mes y año del mes vencido
    mes_borrar = mes_actual - 7
    if mes_borrar <= 0:
        mes_borrar += 12
        anho_vencido = anho_actual - 1
    else:
        anho_vencido = anho_actual
    fecha_borrar = str(anho_vencido)+str(mes_borrar).zfill(2)
    return fecha_borrar



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
    fecha_vencida = str(anho_vencido)+str(mes_vencido).zfill(2)
    return fecha_vencida

# Obtener loggers para este módulo
fecha_mes_vencido_log = fecha_mes_vencido()
_logger, log_file = configurar_logging(fecha_mes_vencido_log, __name__)
_logger_simple = configurar_separador(log_file)

# Declaración de la variable global 
lista_archivos_copiar_1 = []

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


def cliente_sftp(host: str, port: int, username: str, password: str) -> Tuple[paramiko.SFTPClient, paramiko.SSHClient]:
    """
    Establece una conexión SFTP a un servidor remoto utilizando autenticación por contraseña.

    Args:
        host (str): La dirección IP o nombre del host del servidor SFTP.
        port (int): El puerto para conectarse al servidor SFTP.
        username (str): El nombre de usuario para la autenticación SFTP.
        password (str): La contraseña para la autenticación SFTP.

    Returns:
        Tuple[paramiko.SFTPClient, paramiko.SSHClient]:
            - paramiko.SFTPClient: Una instancia del cliente SFTP conectada al servidor.
            - paramiko.SSHClient: Una instancia del cliente SSH utilizado para la conexión.

    Exceptions:
        paramiko.AuthenticationException: Si la autenticación con el servidor falla.
        Exception: Si ocurre cualquier otro error durante la conexión.

    Ejemplo de uso:
        sftp, client = cliente_sftp('example.com', 22, 'usuario', 'contraseña')
        if sftp and client:
            print("Conexión SFTP establecida con éxito")
            # Aquí puedes realizar las operaciones SFTP necesarias
            sftp.close()
            client.close()
    """
    sftp = None

    try:
        # Crear un cliente SSH
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Conectar al servidor utilizando contraseña
        client.connect(hostname=host, port=port, username=username, password=password)

        # Crear cliente SFTP
        sftp = client.open_sftp()
        return sftp, client

    except paramiko.AuthenticationException as e:
        print(f"Fallo de autenticación: {e}")
        return None, None
    except Exception as e:
        print(f"Error general: {e}")
        return None, None
            

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
    _logger_simple.info(f"**********************************************************************************************************************************")
    _logger.info(f"Iniciando el proceso de busqueda de facturas comprimidas en el sftp")
    _logger_simple.info(f"**********************************************************************************************************************************")

    sftp, transport = cliente_sftp(host, port, username, password)
    if not sftp or not transport:
        return None

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
            print(f"Archivo: {archivo} encontrado en el sftp")
            if extraer_fecha(archivo) == fecha_vencida:
                print(f"Fecha del encontrada en el nombre del archivo: {extraer_fecha(archivo)}")
                print(f"Fecha del mes vencido: {fecha_vencida}")
                lista_archivos_copiar.append(archivo)
    print()
    _logger.info(f"Lista total de archivos comprimidos con facturas:")
    for index,file in enumerate(lista_archivos_copiar, start=1):    
        _logger.info(f"{index}. {file}")
    print()
    return lista_archivos_copiar


def eliminar_directorio(sftp, path):
    try:
        # Obtenemos el listado de archivos en el path
        _logger.info(f"Eliminando facturas .pdf dentro del directorio para vaciarlo...")
        for file_attr in sftp.listdir_attr(str(path)):
            filename = file_attr.filename
            dir_path = Path(path)
            filepath = dir_path / filename
            ruta_path = filepath.as_posix()
            if filepath.suffix.lower() == '.pdf':
                # Es un archivo PDF: lo eliminamos
                sftp.remove(ruta_path)
        # Después de vaciar el directorio, lo eliminamos
        _logger.info(f"Directorio vaciado")
        _logger.info(f"Procediendo a eliminacion del directorio")
        sftp.rmdir(str(path))
        _logger.info(f"Directorio eliminado: {path}")
    except IOError as e:
        _logger.error(f"Error al eliminar {path}: {e}")


def borrar_carpeta_6_meses_antes (host, port, username, password) -> None:
    """
    Establece una conexión SSH al servidor SFTP y elimina recursivamente la carpeta de facturas correspondiente
    a hace 6 meses en el servidor remoto.

    La función realiza los siguientes pasos:
    - Calcula la fecha correspondiente a hace 6 meses utilizando `fecha_mes_borrar()`.
    - Establece una conexión SSH mediante `cliente_sftp` para ejecutar comandos en el servidor remoto.
    - Construye el comando de borrado `rm -rf` para eliminar la carpeta y su contenido.
    - Ejecuta el comando en el servidor remoto.
    - Maneja y registra errores si ocurren durante la conexión o la ejecución del comando.
    - Cierra las conexiones SFTP y SSH al finalizar.

    Args:
        host (str): Dirección IP o nombre del host del servidor SFTP.
        port (int): Puerto para conectarse al servidor SFTP.
        username (str): Nombre de usuario para la autenticación SSH.
        password (str): Contraseña para la autenticación SSH.

    Returns:
        None: Esta función no devuelve ningún valor.

    Logs:
        - Info: Mensajes informativos sobre el progreso de la operación.
        - Error: Mensajes de error si ocurre algún problema durante la conexión o eliminación.
        - Debug: Salida del comando de borrado, si está disponible.

    Raises:
        Exception: Registra cualquier excepción ocurrida durante el proceso.

    Ejemplo de uso:
        borrar_carpeta_6_meses_antes('sftp.ejemplo.com', 22, 'usuario', 'contraseña')
    """
    _logger_simple.info(f"**********************************************************************************************************************************")
    _logger.info(f"Iniciando el proceso de busqueda y borrado de facturas con mas de 6 meses.")
    _logger_simple.info(f"**********************************************************************************************************************************")

    sftp = None
    client = None
    fecha_borrar = fecha_mes_borrar()
    path_carpeta_borrar = f"./{fecha_borrar}"
    try:
        _logger.info(f"Estableciendo conexion ssh con el SFTP para el borrado de las facturas de hace 6 meses")
        sftp, client = cliente_sftp(host, port, username, password)
        if client is None:
            _logger.error(f"No se pudo establecer la conexion ssh")
            return
        
        try:
            sftp.stat(path_carpeta_borrar)
            existencia_carpeta = True
        except IOError:
            existencia_carpeta = False
        if existencia_carpeta:
            _logger.info(f"Carpeta {path_carpeta_borrar} encontrada")
            eliminar_directorio(sftp, Path(path_carpeta_borrar))
        else:
            _logger.warning(f"No existe la carpeta {path_carpeta_borrar} en el SFTP")
            _logger.info(f"Cerrando conexion luego de verificar que no existe la carpeta de facturas de hace 6 meses")
        
    except Exception as e:
        _logger.error(f"Error al intentar borrar la carpeta de facturas de hace 6 meses ({path_carpeta_borrar}): {e}")
    finally:
        if sftp:
            sftp.close()
        if client:
            client.close()
        

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
    try:
        print(f"Entrando en la funcion de descarga")
        global lista_archivos_copiar_1
        # Crear el cliente SFTP
        _logger.info("Estableciendo conexion SFTP para descarga")
        sftp, transport = cliente_sftp(host, port, username, password)
        
        lista_archivos_copiar_1 = filtrar_facturas_mes_vencido(conteo_archivos)
            
        # Descargar los archivos que coinciden con los nombres en la lista
        for archivo in lista_archivos_copiar_1:
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
    except Exception as e:
        _logger.error(f"Error en descargar_archivos_sftp: {e}") 
        print(f"Error: {e}")
    
    # Cerrar la conexión SFTP
    _logger.info("Cerrando conexion SFTP debido a terminacion del proceso de descarga")
    sftp.close()
    transport.close()
    

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
                _logger.warning(f"El archivo ZIP: {file_path} ya estaba descomprimido en esa ubicacion")
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
                _logger.warning(f"El archivo RAR: {file_path} ya esta descomprimido")
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
                _logger.warning(f"El archivo TAR.GZ: {file_path} ya esta descomprimido")
                return  # Salir sin extraer nada

            # Extraer los archivos si no están descomprimidos
            _logger.info(f"Descomprimiendo archivo TAR.GZ: {file_path}")
            tar_ref.extractall(output_dir)
        _logger.info(f"Archivo TAR.GZ descomprimido: {file_path}")
    except Exception as e:
        _logger.error(f"Error al descomprimir el archivo TAR.GZ {file_path}: {e}")
            

def descomprimir_archivos(directorio: str) -> str:
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
        raise FileNotFoundError(f"El directorio {directorio} no existe o no es un directorio valido")
    
    output_dir_name = None

    archivos_comprimidos = [
        file for file in dir_path.iterdir()
        if file.suffix in ('.zip', '.rar') or file.name.endswith('.tar.gz')
    ]
    if not archivos_comprimidos:
        _logger.warning("No hay archivos comprimidos validos para descomprimir.")
        return None  # No lanzar error, retornar None

    # Recorrer todos los archivos en el directorio
    for file_path in archivos_comprimidos:
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

    return output_dir_name
            

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
    _logger.info(f"Iniciando deliminacion de descomprimidos")

    # Verificar que el directorio existe
    if not dir_path.exists() or not dir_path.is_dir():
        raise FileNotFoundError(f"El directorio {directorio} no existe o no es un directorio valido")

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
    
    Esta función realiza los siguientes pasos: 
    1. Conectarse al servidor SFTP. 
    2. Buscar la carpeta especificada en el directorio local. 
    3. Si la carpeta se encuentra, verificar si el directorio remoto existe en el servidor SFTP. 
    4. Crear el directorio remoto si no existe. 
    5. Subir los archivos PDF de la carpeta local al directorio remoto en el servidor SFTP. 
    
    Args: 
        host (str): Dirección del servidor SFTP. 
        port (int): Puerto del servidor SFTP. 
        username (str): Nombre de usuario para el acceso SFTP. 
        password (str): Contraseña para el acceso SFTP. 
        carpeta_local (str): Ruta del directorio local donde se buscará la carpeta. 
        carpeta_buscar (str): Nombre de la carpeta a buscar y subir. 
    Returns: 
        None
    """
    sftp, transport = cliente_sftp(host, port, username, password)

    if sftp is None or transport is None:
        _logger.error("No se pudo establecer la conexion SFTP. Abortando subida.")
        return  # Salir de la función
    
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
            if item.is_dir() and item.name == carpeta_buscar:
                _logger.debug(f"Carpeta encontrada: {item}")
                return item
        return None
    
    carpeta_encontrada = buscar_carpeta(carpeta_local_path, carpeta_buscar)
    
    if carpeta_encontrada:
        _logger.info(f"Carpeta {carpeta_encontrada} encontrada y lista para subir su contenido al SFTP")
        try:
            # Obtén la ruta de inicio del usuario
            home_directory = sftp.normalize(".")
            _logger.info(f"La ruta de inicio del usuario SFTP es: {home_directory}")
            
            # Ajusta la ruta remota
            remote_directory_path = f"{home_directory.rstrip('/')}/{carpeta_encontrada.name}"

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

        try:
            cantidad_de_copiados = 0
            cantidad_de_verificados = 0
            # Iterar sobre todos los archivos PDF en la carpeta encontrada
            for pdf_file in carpeta_encontrada.glob('*.pdf'):
                remote_file_path = f"{remote_directory_path}/{pdf_file.name}"                
                sftp.stat(remote_directory_path).st_mode 
                
                # Subir el archivo PDF al SFTP
                try:
                    remote_file_stat = sftp.stat(remote_file_path)
                    remote_file_size = remote_file_stat.st_size
                    local_file_size = pdf_file.stat().st_size
                    cantidad_de_verificados += 1
                    if remote_file_size == local_file_size:
                        print(f"Archivo {remote_file_path} ya existe y tiene el mismo tamaño, no se hace nada y se revisa el siguiente")
                        print("")
                    else:
                        sftp.put(str(pdf_file), remote_file_path)
                        print(f"Archivo {pdf_file} subido a {remote_file_path}")
                        cantidad_de_copiados += 1
                except FileNotFoundError:
                    sftp.put(str(pdf_file), remote_file_path)
                    print(f"Archivo {pdf_file} subido a {remote_file_path}")
                    cantidad_de_verificados += 1
                    cantidad_de_copiados += 1
            sftp.close()
            transport.close()
            
            if cantidad_de_copiados == cantidad_de_verificados:
                _logger.info(f"Carpeta subida exitosamente al sftp")
            else:
                _logger.info(f"Ya la carpeta con las facturas se encontraba subida al sftp")
            
            _logger.info(f"Cantidad de archivos verificados: {cantidad_de_verificados}")
            _logger.info(f"Cantidad de archivos subidos al sftp: {cantidad_de_copiados}")
            _logger.info(f"Proceso finalizado, facturas de Cubacel Online subidas exitosamente al sftp")
        except IOError as e:
            _logger.error(f"Error al subir la carpeta: {e}")
        except Exception as e:
            _logger.error(f"Error inesperado al subir la carpeta: {e}")
    else:
        _logger.warning(f"No se encontro la carpeta {carpeta_buscar} en la carpeta {carpeta_local}")
        sftp.close()
        transport.close()


def ejecutar_descompactar_facturas(host:str , port: int , username_sftp:str, password) -> None:
    """
    Realiza el proceso completo de gestión de facturas comprimidas en un servidor SFTP.
    
    El flujo incluye:
    1. Conexión al servidor SFTP y listado de archivos comprimidos
    2. Notificación por SMS del inicio del proceso
    3. Descarga de archivos (continúa con archivos locales si falla la descarga)
    4. Descompresión de archivos
    5. Re-upload de archivos procesados al servidor SFTP
    6. Manejo de errores parciales con continuidad del proceso

    Args:
        host (str): Dirección del servidor SFTP
        port (int): Puerto del servidor SFTP
        username (str): Nombre de usuario para autenticación SFTP
        password (str): Contraseña para autenticación SFTP

    Returns:
        None: La función no retorna valores pero tiene efectos secundarios:
            - Envía notificaciones por SMS
            - Crea/actualiza el directorio 'archivos_descargados'
            - Modifica el estado del servidor SFTP

    Raises:
        paramiko.ssh_exception.SSHException: Para errores generales de conexión SFTP
        OSError: Para problemas en operaciones de archivo locales
        Exception: Para fallos inesperados en subprocesos críticos

    Notas:
        - Utiliza variables de entorno para configuración sensible (SMS, credenciales)
        - Funciona en modo resiliente: continua el proceso aunque falle alguna subetapa
        - Requiere Python 3.8+ por el uso de pathlib y type hints avanzados
    """
    # Llamar a la configuración global
    # clear_console()
    auth_url = os.getenv("AUTH_URL")
    username_sms = os.getenv("USERNAME_SMS")
    password_sms = os.getenv("PASSWORD_SMS")
    sms_url = os.getenv("SMS_URL")
    token = obtener_token_servidor_sms(auth_url, username_sms, password_sms)
    mensaje_sms = "Comenzando procesamiento de facturas de Cubacel Online"
    destinos = ["51368261","52888880"]
    if token:
        envio_sms(sms_url, token, mensaje_sms, destinos)
    borrar_carpeta_6_meses_antes(host, port, username_sftp, password)
    conteo_archivos = read_from_sftp(host, port, username_sftp, password)
    lista_archivos_copiar = []

    if conteo_archivos is None:
        _logger.error("No se pudo leer el SFTP. Continuando con descompresion de archivos locales (si existen).")
    else:
        _logger.info(f"Lista de archivos .tar.gz encontrados: {conteo_archivos.tar_gz_files}") 
        _logger.info(f"Lista de archivos .zip encontrados: {conteo_archivos.zip_files}") 
        _logger.info(f"Lista de archivos .rar encontrados: {conteo_archivos.rar_files}")
        lista_archivos_copiar = lista_archivos_copiar_1

    # Crear carpeta de descarga (si no existe)
    destino_descarga = "archivos_descargados"
    direccion_destino_descarga = Path.cwd() / destino_descarga
    direccion_destino_descarga.mkdir(parents=True, exist_ok=True)

    # Descargar archivos SOLO si conteo_archivos no es None
    if conteo_archivos is not None:
        descargar_archivos_sftp(conteo_archivos, host, port, username_sftp, password, lista_archivos_copiar, direccion_destino_descarga)
    else:
        _logger.warning("No se descargaron archivos del SFTP (conteo_archivos es None).")

    # Descomprimir y subir (aunque no haya archivos nuevos)
    carpeta_buscar = descomprimir_archivos(direccion_destino_descarga)
    subir_carpeta_a_sftp(host, port, username_sftp, password, destino_descarga, carpeta_buscar)