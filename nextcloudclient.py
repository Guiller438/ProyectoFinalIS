import os
import requests

# ✅ Crea carpeta si no existe
def crear_carpeta_nextcloud(nombre_carpeta):
    base_url = os.getenv("NEXTCLOUD_URL")  # ejemplo: https://nextcloud.jaimendo.tech/remote.php/dav/files/nextcloud
    url = f"{base_url}/{nombre_carpeta}/"
    auth = (os.getenv("NEXTCLOUD_USER"), os.getenv("NEXTCLOUD_PASSWORD"))

    respuesta = requests.request("MKCOL", url, auth=auth)

    if respuesta.status_code in [200, 201, 301, 405]:  # 405 significa "ya existe"
        print(f"📁 Carpeta '{nombre_carpeta}' verificada/creada.")
        return True
    else:
        print(f"❌ Error al crear/verificar carpeta '{nombre_carpeta}': {respuesta.status_code} - {respuesta.text}")
        return False



# ✅ Sube un archivo PDF al directorio remoto
def subir_a_nextcloud(nombre_archivo_local, nombre_remoto):
    base_url = os.getenv("NEXTCLOUD_URL")  # sin barra al final
    if base_url.endswith("/"):
        base_url = base_url[:-1]

    # Construye bien la URL del archivo destino
    nextcloud_url = f"{base_url}/{nombre_remoto}"

    auth = (os.getenv("NEXTCLOUD_USER"), os.getenv("NEXTCLOUD_PASSWORD"))

    with open(nombre_archivo_local, 'rb') as archivo:
        response = requests.put(nextcloud_url, data=archivo, auth=auth)

    if response.status_code in (200, 201, 204):
        print(f"✅ Archivo subido a Nextcloud: {nextcloud_url}")
        return True
    else:
        print(f"❌ Error al subir archivo: {response.status_code} - {response.text}")
        return False
