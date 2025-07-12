import os
import base64
import requests
from dotenv import load_dotenv
from nextcloudclient import subir_a_nextcloud  # Asegúrate que esta función existe y funciona

load_dotenv()

ODOO_URL = os.getenv("ODOO_URL")
ODOO_DB = os.getenv("ODOO_DB")
ODOO_USER = os.getenv("ODOO_USER")
ODOO_PASSWORD = os.getenv("ODOO_PASSWORD")

# -------------------- LOGIN --------------------
def login_odoo():
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "common",
            "method": "login",
            "args": [ODOO_DB, ODOO_USER, ODOO_PASSWORD]
        },
        "id": "login"
    }

    res = requests.post(ODOO_URL, json=payload).json()
    uid = res.get("result")
    if uid is None:
        raise Exception(f"❌ Falló el login en Odoo: {res}")
    print(f"🔐 Login correcto. UID: {uid}")
    return uid

# -------------------- OBTENER FACTURAS --------------------
def obtener_todas_las_facturas(uid):
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [
                ODOO_DB,
                uid,
                ODOO_PASSWORD,
                "account.move",
                "search_read",
                [],  # Sin filtro
                {
                    "fields": ["id", "name", "invoice_date", "amount_total", "partner_id"],
                    "limit": 100
                }
            ]
        },
        "id": "obtener_todas"
    }

    res = requests.post(ODOO_URL, json=payload).json()
    if "error" in res:
        raise Exception(f"❌ Error al obtener facturas: {res['error']}")
    return res.get("result", [])

# -------------------- OBTENER PDFs --------------------
def obtener_pdfs_facturas():
    uid = login_odoo()
    
    # Buscar adjuntos PDF vinculados a account.move
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [
                ODOO_DB,
                uid,
                ODOO_PASSWORD,
                "ir.attachment",
                "search_read",
                [[
                    ["res_model", "=", "account.move"],
                    ["mimetype", "=", "application/pdf"]
                ]],
                {
                    "fields": ["id", "name", "datas"],
                    "limit": 100
                }
            ]
        },
        "id": "leer_pdfs"
    }

    res = requests.post(ODOO_URL, json=payload).json()
    
    if "error" in res:
        raise Exception(f"❌ Error al obtener adjuntos: {res}")

    archivos = res.get("result", [])
    print(f"📎 {len(archivos)} archivos PDF encontrados.")

    os.makedirs("facturas_descargadas", exist_ok=True)
    archivos_locales = []

    for archivo in archivos:
        nombre = archivo["name"]
        contenido_base64 = archivo["datas"]
        ruta_local = os.path.join("facturas_descargadas", nombre)

        with open(ruta_local, "wb") as f:
            f.write(base64.b64decode(contenido_base64))
        
        print(f"✅ PDF guardado localmente: {ruta_local}")
        archivos_locales.append(ruta_local)

    return archivos_locales

# -------------------- SUBIR A NEXTCLOUD --------------------
def subir_todos_a_nextcloud():
    archivos = obtener_pdfs_facturas()
    archivos_subidos = []

    for ruta_local in archivos:
        nombre_remoto = f"facturas/{os.path.basename(ruta_local)}"
        exito = subir_a_nextcloud(ruta_local, nombre_remoto)
        if exito:
            archivos_subidos.append(nombre_remoto)

    return {
        "total_facturas": len(archivos),
        "archivos_subidos": archivos_subidos
    }

def obtener_lineas_factura(uid, factura_id):
    payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [
                ODOO_DB,
                uid,
                ODOO_PASSWORD,
                "account.move.line",
                "search_read",
                [[["move_id", "=", factura_id]]],  # 👈 CORREGIDO: se pasa como una lista de condiciones
                {
                    "fields": ["name", "quantity", "price_unit", "price_subtotal"],
                    "limit": 100
                }
            ]
        },
        "id": "lineas"
    }

    res = requests.post(ODOO_URL, json=payload).json()
    if "error" in res:
        raise Exception(f"❌ Error al obtener líneas de factura {factura_id}: {res['error']}")
    return res.get("result", [])
