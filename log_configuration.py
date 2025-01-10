from pathlib import Path
import logging

# Configuración global de logging
def configurar_logging(fecha:str):
    """
    Configura el sistema de logging para que todos los loggers escriban en el mismo archivo y consola.
    """
    # Directorio y archivo de log
    dir_log = Path("logs")
    dir_log.mkdir(exist_ok=True)  # Asegura que el directorio exista
    log_file = dir_log / f"{fecha}_log_facturas_cubacel_online.log"

    # Configuración del logger raíz
    logger_raiz = logging.getLogger()
    logger_raiz.setLevel(logging.DEBUG)  # Nivel global de logging

    # Formato del log
    formato = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    # Manejador para archivo
    manejador_archivo = logging.FileHandler(log_file)
    manejador_archivo.setLevel(logging.DEBUG)
    manejador_archivo.setFormatter(formato)

    # Manejador para consola
    manejador_consola = logging.StreamHandler()
    manejador_consola.setLevel(logging.DEBUG)
    manejador_consola.setFormatter(formato)

    # Añadir manejadores al logger raíz
    logger_raiz.addHandler(manejador_archivo)
    logger_raiz.addHandler(manejador_consola)
    
    paramiko_logger = logging.getLogger("paramiko")
    paramiko_logger.setLevel(logging.WARNING)  # o el nivel que desees para Paramiko