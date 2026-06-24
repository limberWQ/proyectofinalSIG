from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.utils.auth import staff_required, admin_required
from app.services import chofer_service

choferes_bp = Blueprint("choferes", __name__, url_prefix="/choferes")


@choferes_bp.route("/")
@staff_required
def listar():
    choferes = chofer_service.listar_choferes()
    return render_template("choferes/listar.html", choferes=choferes)


@choferes_bp.route("/crear", methods=["GET", "POST"])
@admin_required
def crear():
    if request.method == "POST":
        try:
            ci = request.form["ci"]
            nombres = request.form["nombres"]
            apellidos = request.form["apellidos"]
            licencia = request.form["licencia"]
            telefono = request.form.get("telefono", "")

            if not ci.strip() or not nombres.strip() or not apellidos.strip() or not licencia.strip():
                raise ValueError("CI, nombres, apellidos y licencia son obligatorios.")

            chofer, username = chofer_service.crear_chofer(ci, nombres, apellidos, licencia, telefono)
            flash(
                f"Chofer registrado correctamente. Se creó su cuenta de acceso al sistema: "
                f"usuario «{username}», contraseña temporal «{chofer.ci}». "
                f"Comunícaselo para que pueda iniciar sesión y transmitir su ubicación durante los viajes.",
                "success",
            )
            return redirect(url_for("choferes.listar"))
        except ValueError as e:
            flash(str(e), "danger")
        except Exception:
            flash("El CI ya existe o los datos son inválidos.", "danger")

    return render_template("choferes/crear.html")


@choferes_bp.route("/editar/<int:id_chofer>", methods=["GET", "POST"])
@admin_required
def editar(id_chofer):
    chofer = chofer_service.obtener_chofer(id_chofer)

    if request.method == "POST":
        try:
            ci = request.form["ci"]
            nombres = request.form["nombres"]
            apellidos = request.form["apellidos"]
            licencia = request.form["licencia"]
            telefono = request.form.get("telefono", "")
            activo = request.form.get("activo") == "on"

            if not ci.strip() or not nombres.strip() or not apellidos.strip() or not licencia.strip():
                raise ValueError("CI, nombres, apellidos y licencia son obligatorios.")

            chofer_service.actualizar_chofer(id_chofer, ci, nombres, apellidos, licencia, telefono, activo)
            flash("Chofer actualizado correctamente.", "success")
            return redirect(url_for("choferes.listar"))
        except ValueError as e:
            flash(str(e), "danger")
        except Exception:
            flash("El CI ya existe o los datos son inválidos.", "danger")

    return render_template("choferes/editar.html", chofer=chofer)


@choferes_bp.route("/eliminar/<int:id_chofer>", methods=["POST"])
@admin_required
def eliminar(id_chofer):
    try:
        chofer_service.eliminar_chofer(id_chofer)
        flash("Chofer eliminado correctamente.", "success")
    except ValueError as e:
        flash(str(e), "danger")
    return redirect(url_for("choferes.listar"))


@choferes_bp.route("/resetear-password/<int:id_chofer>", methods=["POST"])
@admin_required
def resetear_password(id_chofer):
    try:
        chofer_service.resetear_password_chofer(id_chofer)
        flash("Contraseña restablecida al CI del chofer.", "success")
    except ValueError as e:
        flash(str(e), "danger")
    return redirect(url_for("choferes.listar"))
