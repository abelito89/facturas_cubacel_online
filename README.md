# Facturas de CUBACEL ONLINE

Este proyecto es una API desarrollada con **FastAPI** que permite realizar diversas operaciones relacionadas con archivos de facturas almacenados en un servidor SFTP. La API incluye funcionalidades para leer, descargar, descomprimir y subir archivos.

## Estructura del Proyecto

```plaintext
FACTURAS_CUBACEL_ONLINE/
│
├── .env
├── .gitignore
├── script_cubacel_online.py
├── functions.py
├── main.py
├── README.md
├── requirements.txt
├── archivos_descargados/
├── schemas/
│   ├── __pycache__/
│   ├── __init__.py
│   └── schemas.py
└── venv_cubacel/
    └── __init__.py
```

### Descripción de los Archivos y Directorios

- **.env**: Archivo de configuración de entorno con las variables necesarias para la conexión SFTP.
- **.gitignore**: Especifica los archivos y directorios que deben ser ignorados por Git.
- **script_cubacel_online.py**: Script para ejecutar el proceso sin correr la API.
- **functions.py**: Contiene todas las funciones utilizadas por la API.
- **main.py**: Archivo principal que inicia la aplicación FastAPI.
- **README.md**: Este archivo, que proporciona una descripción general del proyecto y las instrucciones para su uso.
- **requirements.txt**: Lista de dependencias necesarias para ejecutar el proyecto.
- **archivos_descargados/**: Directorio donde se almacenan los archivos descargados.
- **schemas/**: Contiene los esquemas de datos utilizados en el proyecto.
  - **schemas/__pycache__/**: Archivos cacheados de Python.
  - **schemas/__init__.py**: Marca el directorio como un paquete Python.
  - **schemas/schemas.py**: Define los esquemas de datos utilizados.
- **venv_cubacel/**: Entorno virtual para el proyecto.
  - **venv_cubacel/__init__.py**: Marca el directorio como un paquete Python.

## Instalación

Sigue estos pasos para instalar y configurar el proyecto en tu entorno local.

### 1. Clonar el Repositorio

```sh
git clone https://github.com/tu_usuario/nombre_del_proyecto.git
cd nombre_del_proyecto
```

### 2. Crear y Activar un Entorno Virtual (Opcional pero Recomendado)

#### Windows

```sh
python -m venv env
.\env\Scripts\activate
```

#### macOS y Linux

```sh
python3 -m venv env
source env/bin/activate
```

### 3. Instalar las Dependencias

```sh
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto y agrega las siguientes variables de entorno:

```env
IP_FTP=tu_ip
PORT=tu_puerto
USER=tu_usuario
PASSWORD=tu_contraseña
```

## Uso

Para iniciar la aplicación FastAPI, ejecuta el siguiente comando:

```sh
uvicorn main:app --reload
```

La API estará disponible en `http://127.0.0.1:8000`.

## Endpoints

### `GET /decompactar_facturas`

Descomprime los archivos de facturas almacenados en el servidor SFTP y los sube nuevamente.

#### Parámetros
- `host`: Dirección del servidor SFTP.
- `port`: Puerto del servidor SFTP.
- `username`: Nombre de usuario para el acceso SFTP.
- `password`: Contraseña para el acceso SFTP.

## Detalles de las Funciones

Las funciones principales utilizadas por la API se encuentran en el archivo `functions.py`. A continuación, se detallan algunas de las más importantes:

### `read_from_sftp`

Lee el contenido del servidor SFTP y cuenta los archivos .tar.gz, .zip, y .rar.

### `filtrar_facturas_mes_vencido`

Filtra los archivos de facturas que corresponden al mes vencido.

### `clear_console`

Limpia la consola.

### `descargar_archivos_sftp`

Descarga los archivos seleccionados desde el servidor SFTP.

### `descomprimir_archivos`

Descomprime los archivos descargados.

### `eliminar_comprimidos`

Elimina los archivos comprimidos una vez descomprimidos.

### `subir_carpeta_a_sftp`

Sube una carpeta específica al servidor SFTP.

## Esquemas de Datos

### `ConteoArchivos`

Modelo para contar archivos específicos en un servidor SFTP.

```python
from pydantic import BaseModel
from typing import List

class ConteoArchivos(BaseModel):
    tar_gz_files: List[str]
    zip_files: List[str]
    rar_files: List[str]
```

## Contribución

Si deseas contribuir a este proyecto, por favor sigue los siguientes pasos:

1. Haz un fork del repositorio.
2. Crea una nueva rama (`git checkout -b feature/nueva_funcionalidad`).
3. Realiza tus cambios y haz commit (`git commit -am 'Añadir nueva funcionalidad'`).
4. Sube tus cambios (`git push origin feature/nueva_funcionalidad`).
5. Abre un Pull Request.


```

Este `README.md` ahora incluye una descripción detallada de la estructura del proyecto, asegurando que cualquier usuario pueda seguir los pasos necesarios independientemente de su plataforma. Si necesitas más ajustes o detalles adicionales, no dudes en decírmelo. ¡Buena suerte con tu proyecto!