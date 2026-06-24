from app import db
from app.models.chofer import Chofer
from app.models.usuario import Usuario


def listar_choferes():
    return Chofer.query.order_by(Chofer.id_chofer.desc()).all()


def obtener_chofer(id_chofer):
    return Chofer.query.get_or_404(id_chofer)


def _generar_username_disponible(ci):
    """El CI se usa como nombre de usuario; si ya existe, se agrega un sufijo."""
    base = ci.strip()
    username = base
    sufijo = 1
    while Usuario.query.filter_by(usuario=username).first() is not None:
        sufijo += 1
        username = f"{base}-{sufijo}"
    return username


def crear_chofer(ci, nombres, apellidos, licencia, telefono):
    """
    Crea el chofer y, automáticamente, su cuenta de usuario con rol 'chofer'.
    El nombre de usuario es el CI y la contraseña inicial también es el CI
    (contraseña temporal que el chofer debería cambiar; se informa al admin
    al momento de la creación).
    """
    ci = ci.strip()

    chofer = Chofer(
        ci=ci,
        nombres=nombres.strip(),
        apellidos=apellidos.strip(),
        licencia=licencia.strip(),
        telefono=(telefono or "").strip(),
    )

    username = _generar_username_disponible(ci)
    usuario = Usuario(
        usuario=username,
        nombre=f"{nombres.strip()} {apellidos.strip()}",
        rol="chofer",
    )
    usuario.set_password(ci)  # contraseña temporal = CI
    db.session.add(usuario)
    db.session.flush()  # para obtener id_usuario

    chofer.id_usuario = usuario.id_usuario
    db.session.add(chofer)
    db.session.commit()
    return chofer, username


def actualizar_chofer(id_chofer, ci, nombres, apellidos, licencia, telefono, activo):
    chofer = obtener_chofer(id_chofer)
    chofer.ci = ci.strip()
    chofer.nombres = nombres.strip()
    chofer.apellidos = apellidos.strip()
    chofer.licencia = licencia.strip()
    chofer.telefono = (telefono or "").strip()
    chofer.activo = activo

    # Mantener sincronizado el nombre y el estado activo de la cuenta de usuario asociada
    if chofer.usuario:
        chofer.usuario.nombre = f"{chofer.nombres} {chofer.apellidos}"
        chofer.usuario.activo = activo

    db.session.commit()
    return chofer


def resetear_password_chofer(id_chofer):
    """Restablece la contraseña del chofer a su CI (útil si olvida su clave)."""
    chofer = obtener_chofer(id_chofer)
    if not chofer.usuario:
        raise ValueError("Este chofer no tiene una cuenta de usuario asociada.")
    chofer.usuario.set_password(chofer.ci)
    db.session.commit()


def eliminar_chofer(id_chofer):
    chofer = obtener_chofer(id_chofer)
    if chofer.viajes:
        raise ValueError("No se puede eliminar el chofer: tiene viajes asociados.")
    usuario = chofer.usuario
    db.session.delete(chofer)
    if usuario:
        db.session.delete(usuario)
    db.session.commit()
