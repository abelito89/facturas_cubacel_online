from pathlib import Path
import logging

# Configuración global de logging
def configurar_logging(fecha: str):
    """
    Configura el sistema de logging para que todos los loggers escriban en el mismo archivo y consola.
    """
    # Directorio y archivo de log
    dir_log = Path("logs")
    dir_log.mkdir(exist_ok=True)
    log_file = dir_log / f"{fecha}_log_facturas_cubacel_online.log"

    # Generar un nombre de archivo único si el archivo ya existe
    if log_file.exists():
        counter = 1
        while log_file.exists():
            log_file = dir_log / f"{fecha}_log_facturas_cubacel_online_{counter}.log"
            counter += 1

    # Configuración del logger raíz
    logger_raiz = logging.getLogger()
    logger_raiz.setLevel(logging.DEBUG)

    formato_completo = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    formato_simple = logging.Formatter("%(message)s")

    manejador_archivo = logging.FileHandler(log_file)
    manejador_archivo.setLevel(logging.DEBUG)
    manejador_archivo.setFormatter(formato_completo)

    manejador_consola = logging.StreamHandler()
    manejador_consola.setLevel(logging.DEBUG)
    manejador_consola.setFormatter(formato_completo)

    # Eliminar manejadores duplicados
    if logger_raiz.hasHandlers():
        logger_raiz.handlers.clear()

    logger_raiz.addHandler(manejador_archivo)
    logger_raiz.addHandler(manejador_consola)

    # Configuración simple para logs
    logger_simple = logging.getLogger("simple")
    logger_simple.setLevel(logging.INFO)

    # Eliminar manejadores duplicados
    if logger_simple.hasHandlers():
        logger_simple.handlers.clear()

    manejador_simple = logging.FileHandler(log_file)
    manejador_simple.setLevel(logging.INFO)
    manejador_simple.setFormatter(formato_simple)
    logger_simple.addHandler(manejador_simple)

    paramiko_logger = logging.getLogger("paramiko")
    paramiko_logger.setLevel(logging.WARNING)
