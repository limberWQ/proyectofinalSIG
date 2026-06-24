from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.models.usuario import Usuario

auth_bp = Blueprint("auth", __name__, url_prefix="")


def _redireccion_segun_rol():
    if session.get("rol") == "chofer":
        return redirect(url_for("chofer_panel.mis_viajes"))
    return redirect(url_for("dashboard.index"))


@auth_bp.route("/", methods=["GET"])
def raiz():
    if "id_usuario" in session:
        return _redireccion_segun_rol()
    return redirect(url_for("auth.login"))


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if "id_usuario" in session:
        return _redireccion_segun_rol()

    if request.method == "POST":
        usuario_str = request.form.get("usuario", "").strip()
        password = request.form.get("password", "")

        usuario = Usuario.query.filter_by(usuario=usuario_str).first()

        if usuario and usuario.activo and usuario.check_password(password):
            session["id_usuario"] = usuario.id_usuario
            session["usuario"] = usuario.usuario
            session["nombre"] = usuario.nombre
            session["rol"] = usuario.rol
            flash(f"Bienvenido, {usuario.nombre}.", "success")
            return _redireccion_segun_rol()

        flash("Usuario o contraseña incorrectos.", "danger")

    return render_template("auth/login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("Sesión cerrada correctamente.", "info")
    return redirect(url_for("auth.login"))
