from datetime import datetime
from flask import Blueprint, request, jsonify, session
from app import db
from app.models.viaje import Viaje
from app.models.chofer import Chofer
from app.models.posicion_gps import PosicionGps

gps_bp = Blueprint("gps", __name__, url_prefix="/gps")


def _chofer_de_la_sesion():
    """Obtiene el registro de Chofer vinculado al usuario actualmente logueado."""
    if session.get("rol") != "chofer":
        return None
    return Chofer.query.filter_by(id_usuario=session.get("id_usuario")).first()


@gps_bp.route("/actualizar-posicion", methods=["POST"])
def actualizar_posicion():
    """
    Recibe la posición real transmitida desde el celular del chofer.
    Seguridad: requiere sesión activa con rol 'chofer' (autenticación normal
    del sistema) y que el viaje indicado esté efectivamente asignado a ese
    chofer; ningún otro rol ni chofer ajeno al viaje puede reportar posición.
    """
    chofer = _chofer_de_la_sesion()
    if chofer is None:
        return jsonify({"ok": False, "error": "Debes iniciar sesión como chofer para transmitir tu ubicación."}), 401

    data = request.get_json(silent=True) or {}
    id_viaje = data.get("id_viaje")
    lat = data.get("lat")
    lng = data.get("lng")
    precision = data.get("precision")

    if not id_viaje or lat is None or lng is None:
        return jsonify({"ok": False, "error": "Datos incompletos."}), 400

    viaje = Viaje.query.get(id_viaje)
    if viaje is None or viaje.id_chofer != chofer.id_chofer:
        return jsonify({"ok": False, "error": "Este viaje no está asignado a tu usuario."}), 403

    posicion = PosicionGps.query.filter_by(id_viaje=viaje.id_viaje).first()
    if posicion is None:
        posicion = PosicionGps(id_viaje=viaje.id_viaje)
        db.session.add(posicion)

    posicion.latitud = float(lat)
    posicion.longitud = float(lng)
    posicion.precision_metros = float(precision) if precision is not None else None
    posicion.actualizado_en = datetime.now()
    db.session.commit()

    return jsonify({"ok": True})
