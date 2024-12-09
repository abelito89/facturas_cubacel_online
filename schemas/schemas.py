from pydantic import BaseModel
from typing import List

class ConteoArchivos(BaseModel):
    """    
    Modelo para contar archivos específicos en un servidor SFTP.

    Attributes:
        tar_gz_files (List[str]): Lista de nombres de archivos .tar.gz encontrados.
        zip_files (List[str]): Lista de nombres de archivos .zip encontrados.
        rar_files (List[str]): Lista de nombres de archivos .rar encontrados.
    """
    tar_gz_files: List[str]
    zip_files: List[str]
    rar_files: List[str]