from datetime import date
from flask import Blueprint, render_template, jsonify
from app.utils.auth import staff_required
from app.models.viaje import Viaje

flota_bp = Blueprint("flota", __name__, url_prefix="/flota")


@flota_bp.route("/")
@staff_required
def monitoreo():
    return render_template("flota/monitoreo.html")


@flota_bp.route("/datos")
@staff_required
def datos():
    """
    Devuelve en JSON todos los viajes del día que tienen ruta asignada,
    para representarlos simultáneamente en el panel de monitoreo de flota.
    """
    viajes = Viaje.query.filter_by(fecha_viaje=date.today()).all()

    resultado = []
    for v in viajes:
        if v.ruta is None:
            continue

        posicion_real = None
        if v.posicion_gps:
            posicion_real = {
                "lat": v.posicion_gps.latitud,
                "lng": v.posicion_gps.longitud,
                "actualizado_en": v.posicion_gps.actualizado_en.strftime("%H:%M:%S"),
            }

        resultado.append({
            "id_viaje": v.id_viaje,
            "id_ruta": v.ruta.id_ruta,
            "origen": v.origen,
            "destino": v.destino,
            "hora_salida": v.hora_salida.strftime("%H:%M"),
            "bus": v.bus.placa,
            "chofer": v.chofer.nombre_completo,
            "estado": v.estado,
            "asientos_disponibles": v.asientos_disponibles,
            "asientos_total": len(v.viaje_asientos),
            "puntos": v.ruta.puntos,
            "posicion_real": posicion_real,
        })

    return jsonify({"viajes": resultado})


@flota_bp.route("/posicion/<int:id_viaje>")
@staff_required
def posicion(id_viaje):
    """Devuelve solo la última posición real conocida de un viaje (refresco rápido)."""
    viaje = Viaje.query.get_or_404(id_viaje)
    if not viaje.posicion_gps:
        return jsonify({"disponible": False})
    return jsonify({
        "disponible": True,
        "lat": viaje.posicion_gps.latitud,
        "lng": viaje.posicion_gps.longitud,
        "actualizado_en": viaje.posicion_gps.actualizado_en.strftime("%H:%M:%S"),
    })
