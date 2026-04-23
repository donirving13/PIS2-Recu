"""
ReVIP - Plataforma de Reservaciones con Trust Score
Patrón de Diseño: Proxy (Control de Acceso)
"""

from flask import Flask, render_template, request, redirect, url_for, flash
import json
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "revip-secreto-2024"

RUTA_ESTABLECIMIENTOS = "datos/establecimientos.json"
RUTA_RESERVACIONES    = "datos/reservaciones.json"
RUTA_CLIENTES         = "datos/clientes.json"

def cargar(ruta):
    if not os.path.exists(ruta):
        return []
    with open(ruta, "r", encoding="utf-8") as f:
        return json.load(f)

def guardar(ruta, datos):
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)


# ═══════════════════════════════════════════════════════════════════════════════
#  PATRÓN PROXY
# ═══════════════════════════════════════════════════════════════════════════════

class IServicioReserva:
    """Interfaz común para Proxy y Servicio Real."""
    def solicitar_reserva(self, datos):
        raise NotImplementedError


class ServicioReservaReal(IServicioReserva):
    """Registra la reservación una vez que el Proxy autoriza el acceso."""
    def solicitar_reserva(self, datos):
        reservaciones = cargar(RUTA_RESERVACIONES)
        nueva = {
            "id":              len(reservaciones) + 1,
            "cliente_id":      datos["cliente_id"],
            "establecimiento": datos["establecimiento"],
            "fecha":           datos["fecha"],
            "hora":            datos["hora"],
            "personas":        datos["personas"],
            "creada_en":       datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
        reservaciones.append(nueva)
        guardar(RUTA_RESERVACIONES, reservaciones)
        return {"exito": True, "reservacion": nueva}


class ReservaProxy(IServicioReserva):
    """
    Proxy de Protección: intercepta la solicitud, valida el Trust Score
    y solo delega al ServicioReservaReal si el cliente es apto.
    """
    def __init__(self):
        self._servicio_real = ServicioReservaReal()

    def _verificar_trust_score(self, cliente_id, umbral):
        clientes = cargar(RUTA_CLIENTES)
        cliente = next((c for c in clientes if c["id"] == cliente_id), None)
        if not cliente:
            return False, 0
        return cliente["trust_score"] >= umbral, cliente["trust_score"]

    def solicitar_reserva(self, datos):
        establecimientos = cargar(RUTA_ESTABLECIMIENTOS)
        est = next((e for e in establecimientos if e["nombre"] == datos["establecimiento"]), None)

        if not est:
            return {"exito": False, "motivo": "Establecimiento no encontrado."}

        apto, score_actual = self._verificar_trust_score(datos["cliente_id"], est["umbral_trust"])

        if not apto:
            return {
                "exito": False,
                "motivo": (
                    f"Tu Trust Score ({score_actual}) es menor al mínimo requerido "
                    f"({est['umbral_trust']}) para reservar en {est['nombre']}."
                ),
            }

        return self._servicio_real.solicitar_reserva(datos)


# ═══════════════════════════════════════════════════════════════════════════════
#  RUTAS
# ═══════════════════════════════════════════════════════════════════════════════

@app.route("/")
def inicio():
    return render_template("inicio.html")


@app.route("/registrar-establecimiento", methods=["GET", "POST"])
def registrar_establecimiento():
    if request.method == "POST":
        nombre      = request.form["nombre"].strip()
        ubicacion   = request.form["ubicacion"].strip()
        horario     = request.form["horario"].strip()
        capacidad   = int(request.form["capacidad"])
        umbral      = int(request.form["umbral_trust"])
        descripcion = request.form["descripcion"].strip()

        establecimientos = cargar(RUTA_ESTABLECIMIENTOS)
        if any(e["nombre"].lower() == nombre.lower() for e in establecimientos):
            flash("Ya existe un establecimiento con ese nombre.", "error")
            return redirect(url_for("registrar_establecimiento"))

        nuevo = {
            "id":            len(establecimientos) + 1,
            "nombre":        nombre,
            "ubicacion":     ubicacion,
            "horario":       horario,
            "capacidad":     capacidad,
            "umbral_trust":  umbral,
            "descripcion":   descripcion,
            "registrado_en": datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
        establecimientos.append(nuevo)
        guardar(RUTA_ESTABLECIMIENTOS, establecimientos)
        flash(f'Establecimiento "{nombre}" registrado exitosamente.', "exito")
        return redirect(url_for("lista_establecimientos"))

    return render_template("registrar_establecimiento.html")


@app.route("/establecimientos")
def lista_establecimientos():
    establecimientos = cargar(RUTA_ESTABLECIMIENTOS)
    return render_template("lista_establecimientos.html", establecimientos=establecimientos)


@app.route("/reservar", methods=["GET", "POST"])
def realizar_reservacion():
    establecimientos = cargar(RUTA_ESTABLECIMIENTOS)
    clientes         = cargar(RUTA_CLIENTES)

    if request.method == "POST":
        proxy = ReservaProxy()
        datos = {
            "cliente_id":      request.form["cliente_id"],
            "establecimiento": request.form["establecimiento"],
            "fecha":           request.form["fecha"],
            "hora":            request.form["hora"],
            "personas":        int(request.form["personas"]),
        }
        resultado = proxy.solicitar_reserva(datos)
        if resultado["exito"]:
            flash("¡Reservación confirmada exitosamente!", "exito")
        else:
            flash(resultado["motivo"], "error")
        return redirect(url_for("realizar_reservacion"))

    return render_template("reservar.html", establecimientos=establecimientos, clientes=clientes)


@app.route("/reservaciones")
def lista_reservaciones():
    reservaciones    = cargar(RUTA_RESERVACIONES)
    clientes         = cargar(RUTA_CLIENTES)
    return render_template("lista_reservaciones.html", reservaciones=reservaciones, clientes=clientes)


def inicializar_datos():
    os.makedirs("datos", exist_ok=True)
    if not os.path.exists(RUTA_CLIENTES):
        guardar(RUTA_CLIENTES, [
            {"id": "C001", "nombre": "Ana García",    "trust_score": 85},
            {"id": "C002", "nombre": "Luis Martínez", "trust_score": 45},
            {"id": "C003", "nombre": "Sofía Ruiz",    "trust_score": 95},
        ])
    if not os.path.exists(RUTA_ESTABLECIMIENTOS):
        guardar(RUTA_ESTABLECIMIENTOS, [])
    if not os.path.exists(RUTA_RESERVACIONES):
        guardar(RUTA_RESERVACIONES, [])

if __name__ == "__main__":
    inicializar_datos()
    app.run(debug=True)
