from datetime import date
from flask import Blueprint, render_template, redirect, url_for, flash, session, abort
from app.utils.auth import chofer_required
from app.models.chofer import Chofer
from app.models.viaje import Viaje

chofer_panel_bp = Blueprint("chofer_panel", __name__, url_prefix="/mi-panel")


def _chofer_actual():
    return Chofer.query.filter_by(id_usuario=session.get("id_usuario")).first()


@chofer_panel_bp.route("/")
@chofer_required
def mis_viajes():
    """Lista los viajes programados (hoy y futuros) del chofer autenticado."""
    chofer = _chofer_actual()
    if chofer is None:
        flash("Tu usuario no está vinculado a ningún registro de chofer.", "danger")
        return redirect(url_for("auth.logout"))

    viajes = (
        Viaje.query.filter(
            Viaje.id_chofer == chofer.id_chofer,
            Viaje.fecha_viaje >= date.today(),
            Viaje.estado == "programado",
        )
        .order_by(Viaje.fecha_viaje, Viaje.hora_salida)
        .all()
    )
    return render_template("chofer/mis_viajes.html", viajes=viajes, chofer=chofer)


@chofer_panel_bp.route("/viaje/<int:id_viaje>")
@chofer_required
def ver_viaje(id_viaje):
    """Mapa del viaje con la ruta real y el botón de transmisión GPS."""
    chofer = _chofer_actual()
    viaje = Viaje.query.get_or_404(id_viaje)

    if chofer is None or viaje.id_chofer != chofer.id_chofer:
        abort(403)

    return render_template("chofer/ver_viaje.html", viaje=viaje)
