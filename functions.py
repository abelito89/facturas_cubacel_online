import paramiko


def read_from_sftp(host, port, username, password):
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

    return archivos_tar_gz, archivos_zip, archivos_rar
