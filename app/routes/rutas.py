import json
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.utils.auth import admin_required, staff_required
from app.utils.helpers import to_float
from app.services import ruta_service, viaje_service

rutas_bp = Blueprint("rutas", __name__, url_prefix="/rutas")


@rutas_bp.route("/")
@staff_required
def listar():
    rutas = ruta_service.listar_rutas()
    return render_template("rutas/listar.html", rutas=rutas)


@rutas_bp.route("/crear", methods=["GET", "POST"])
@admin_required
def crear():
    # Solo viajes que todavía no tienen ruta asignada
    viajes = [v for v in viaje_service.listar_viajes() if v.ruta is None]

    if request.method == "POST":
        try:
            id_viaje = int(request.form["id_viaje"])
            nombre = request.form["nombre"]
            puntos = json.loads(request.form.get("puntos", "[]"))
            origen_texto = request.form.get("origen_texto", "")
            destino_texto = request.form.get("destino_texto", "")
            distancia_km = to_float(request.form.get("distancia_km"), None)
            duracion_min = to_float(request.form.get("duracion_min"), None)

            if not nombre.strip():
                raise ValueError("El nombre de la ruta es obligatorio.")

            ruta_service.crear_ruta(
                id_viaje, nombre, puntos, origen_texto, destino_texto, distancia_km, duracion_min
            )
            flash("Ruta calculada y guardada correctamente.", "success")
            return redirect(url_for("rutas.listar"))
        except ValueError as e:
            flash(str(e), "danger")
        except Exception:
            flash("No se pudo guardar la ruta. Verifica los datos e intenta de nuevo.", "danger")

    return render_template("rutas/crear.html", viajes=viajes)


@rutas_bp.route("/editar/<int:id_ruta>", methods=["GET", "POST"])
@admin_required
def editar(id_ruta):
    ruta = ruta_service.obtener_ruta(id_ruta)

    if request.method == "POST":
        try:
            nombre = request.form["nombre"]
            puntos = json.loads(request.form.get("puntos", "[]"))
            origen_texto = request.form.get("origen_texto", "")
            destino_texto = request.form.get("destino_texto", "")
            distancia_km = to_float(request.form.get("distancia_km"), None)
            duracion_min = to_float(request.form.get("duracion_min"), None)

            if not nombre.strip():
                raise ValueError("El nombre de la ruta es obligatorio.")

            ruta_service.actualizar_ruta(
                id_ruta, nombre, puntos, origen_texto, destino_texto, distancia_km, duracion_min
            )
            flash("Ruta actualizada correctamente.", "success")
            return redirect(url_for("rutas.listar"))
        except ValueError as e:
            flash(str(e), "danger")
        except Exception:
            flash("No se pudo actualizar la ruta. Verifica los datos.", "danger")

    return render_template("rutas/editar.html", ruta=ruta)


@rutas_bp.route("/eliminar/<int:id_ruta>", methods=["POST"])
@admin_required
def eliminar(id_ruta):
    try:
        ruta_service.eliminar_ruta(id_ruta)
        flash("Ruta eliminada correctamente.", "success")
    except ValueError as e:
        flash(str(e), "danger")
    return redirect(url_for("rutas.listar"))


@rutas_bp.route("/<int:id_ruta>/datos")
@staff_required
def datos(id_ruta):
    """Devuelve los puntos de la ruta en JSON para pintarla en el mapa."""
    ruta = ruta_service.obtener_ruta(id_ruta)
    return jsonify({
        "nombre": ruta.nombre,
        "puntos": ruta.puntos,
        "origen_texto": ruta.origen_texto,
        "destino_texto": ruta.destino_texto,
        "distancia_km": ruta.distancia_km,
        "duracion_min": ruta.duracion_min,
        "viaje": {
            "origen": ruta.viaje.origen,
            "destino": ruta.viaje.destino,
            "bus": ruta.viaje.bus.placa,
            "chofer": ruta.viaje.chofer.nombre_completo,
            "estado": ruta.viaje.estado,
        },
    })
