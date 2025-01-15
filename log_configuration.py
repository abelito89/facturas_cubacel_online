from pathlib import Path
import logging

def crear_log(fecha: str):
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
def configurar_logging(fecha: str):
    """
    Configura el sistema de logging para que todos los loggers escriban en el mismo archivo y consola.
    """
    log_file = crear_log(fecha)

    formato_completo = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    manejador_archivo = logging.FileHandler(log_file)
    manejador_archivo.setFormatter(formato_completo)

    manejador_consola = logging.StreamHandler()
    manejador_consola.setFormatter(formato_completo)

    _logger = logging.getLogger(__name__)
    _logger.setLevel(level=logging.INFO)
    _logger.addHandler(manejador_archivo)
    _logger.addHandler(manejador_consola)

    return _logger


def configurar_separador(fecha: str):
    """
    Configura el sistema de logging para que todos los loggers escriban en el mismo archivo y consola.
    """
    log_file = crear_log(fecha)

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

