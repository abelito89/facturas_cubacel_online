from pathlib import Path
import logging

def crear_log(fecha: str) -> Path:
    """
    Crea y retorna una ruta de archivo de log basada en la fecha proporcionada. 
    Si un archivo de log con el nombre generado ya existe, añade un sufijo numérico para evitar sobrescribir archivos existentes. 
    
    Parámetros: 
    ---------- 
    fecha : str 
        La fecha a usar en el nombre del archivo de log. Debe estar en un formato que sea compatible con los nombres de archivos, como 'YYYYMM'. 
    
    Retorna: 
    ------- 
    log_file : pathlib.Path 
        La ruta completa al archivo de log creado, asegurando que no sobrescribe archivos existentes. 
        
    Ejemplo: 
    -------- 
    >>> crear_log('202501') PosixPath('logs/202501_log_facturas_cubacel_online.log')
    """
    dir_log = Path("logs")
    dir_log.mkdir(exist_ok=True)
    log_file = dir_log / f"{fecha}_log_facturas_cubacel_online.log"
    # Evitar sobreescribir archivos existentes
    if log_file.exists():
        counter = 1
        while log_file.exists():
            log_file = dir_log / f"{fecha}_log_facturas_cubacel_online({counter}).log"
            counter += 1
    return log_file

# Configuración global de logging
def configurar_logging(fecha: str, name:str) -> tuple[logging.Logger, Path]:
    """
    Configura el sistema de logging para que todos los loggers escriban en el mismo archivo y consola. 
    
    Parámetros: 
    ---------- 
    fecha : str 
        La fecha a usar en el nombre del archivo de log. Debe estar en un formato que sea compatible con los nombres de archivos, como 'YYYYMM'. 
    name : str 
        El nombre del logger que se va a crear.
    
    Retorna: 
    ------- 
    _logger : logging.Logger 
        El logger configurado con los manejadores y formateadores apropiados. 
    log_file : pathlib.Path 
        La ruta completa al archivo de log creado, asegurando que no sobrescribe archivos existentes.
 
    Ejemplo: 
    -------- 
    >>> configurar_logging('202501', 'mi_logger') (<Logger mi_logger (INFO)>, PosixPath('logs/202501_log_facturas_cubacel_online.log'))
    """
    log_file = crear_log(fecha)

    formato_completo = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    manejador_archivo = logging.FileHandler(log_file)
    manejador_archivo.setFormatter(formato_completo)

    manejador_consola = logging.StreamHandler()
    manejador_consola.setFormatter(formato_completo)

    _logger = logging.getLogger(name)
    _logger.setLevel(level=logging.INFO)
    _logger.addHandler(manejador_archivo)
    _logger.addHandler(manejador_consola)

    return _logger, log_file


def configurar_separador(log_file: Path) -> logging.Logger:
    """
    Configura un logger específico para escribir separadores visuales en el archivo de log y en la consola. 
    
    Parámetros: 
    ---------- 
    log_file : pathlib.Path 
        La ruta al archivo de log donde se escribirán los separadores visuales. 
    
    Retorna: 
    ------- 
    _logger_separador : logging.Logger 
        El logger configurado para escribir separadores visuales con el formato especificado. 
    
    Ejemplo: 
    -------- 
    >>> log_file = Path('logs/202501_log_facturas_cubacel_online.log') 
    >>> configurar_separador(log_file) 
    <Logger separador (INFO)>
    """
    formato_separador = logging.Formatter("")
    manejador_archivo_separador = logging.FileHandler(log_file)
    manejador_archivo_separador.setFormatter(formato_separador)

    manejador_consola_separador = logging.StreamHandler()
    manejador_consola_separador.setFormatter(formato_separador)

    _logger_separador = logging.getLogger("separador")
    _logger_separador.setLevel(level=logging.INFO)
    _logger_separador.addHandler(manejador_archivo_separador)
    _logger_separador.addHandler(manejador_consola_separador)

    return _logger_separador

