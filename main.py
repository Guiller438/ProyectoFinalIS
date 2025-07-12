from fastapi import FastAPI
from odoo_client import obtener_pdfs_facturas, obtener_todas_las_facturas, login_odoo, obtener_lineas_factura
from pdfgenerator import generar_pdf
from nextcloudclient import subir_a_nextcloud, crear_carpeta_nextcloud
from typing import List
import os
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

app = FastAPI()

uid = login_odoo()

def tarea_subida_facturas():
    try:
        print(f"⏰ Ejecutando subida automática de facturas - {datetime.now()}")
        carpeta = "facturas"
        crear_carpeta_nextcloud(carpeta)

        facturas = obtener_todas_las_facturas(uid)
        for factura in facturas:
            lineas = obtener_lineas_factura(uid, factura["id"])
            ruta_pdf = generar_pdf(factura, lineas)
            nombre_remoto = f"{carpeta}/{os.path.basename(ruta_pdf)}"
            subir_a_nextcloud(ruta_pdf, nombre_remoto)

        print("✅ Subida automática completada.")
    except Exception as e:
        print(f"❌ Error en tarea programada: {str(e)}")

# Programador en segundo plano
scheduler = BackgroundScheduler()
scheduler.add_job(tarea_subida_facturas, 'interval', seconds=30)  # cada 1 hora
scheduler.start()

@app.get("/facturas", summary="Obtener todas las facturas desde Odoo")
def get_facturas():
    try:
        facturas = obtener_todas_las_facturas(uid)
        return {"total": len(facturas), "facturas": facturas}
    except Exception as e:
        return {"error": str(e)}

@app.post("/facturas/pdf", summary="Generar PDFs de todas las facturas")
def generar_pdfs():
    try:
        facturas = obtener_todas_las_facturas(uid)
        rutas_generadas: List[str] = []
        for factura in facturas:
            lineas = obtener_lineas_factura(uid, factura["id"])
            ruta = generar_pdf(factura, lineas)
            rutas_generadas.append(ruta)
        return {"archivos_generados": rutas_generadas}
    except Exception as e:
        return {"error": f"❌ Error al generar los PDFs: {str(e)}"}

@app.post("/facturas/subir", summary="Generar y subir PDFs a Nextcloud")
def subir_facturas_a_nextcloud():
    try:
        carpeta = "facturas"
        carpeta_creada = crear_carpeta_nextcloud(carpeta)

        if not carpeta_creada:
            return {"error": "❌ No se pudo crear/verificar la carpeta en Nextcloud."}

        facturas = obtener_todas_las_facturas(uid)
        archivos_subidos = []

        for factura in facturas:
            lineas = obtener_lineas_factura(uid, factura["id"])
            ruta_pdf = generar_pdf(factura, lineas)
            nombre_remoto = f"{carpeta}/{os.path.basename(ruta_pdf)}"
            exito = subir_a_nextcloud(ruta_pdf, nombre_remoto)
            if exito:
                archivos_subidos.append(nombre_remoto)

        return {
            "total_facturas": len(facturas),
            "archivos_subidos": archivos_subidos
        }

    except Exception as e:
        return {"error": f"❌ Error al subir PDFs a Nextcloud: {str(e)}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

