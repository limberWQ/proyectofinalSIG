from app import db
from app.models.ruta import Ruta
from app.models.viaje import Viaje


def listar_rutas():
    return Ruta.query.order_by(Ruta.id_ruta.desc()).all()


def obtener_ruta(id_ruta):
    return Ruta.query.get_or_404(id_ruta)


def obtener_ruta_por_viaje(id_viaje):
    return Ruta.query.filter_by(id_viaje=id_viaje).first()


def crear_ruta(id_viaje, nombre, puntos, origen_texto=None, destino_texto=None,
               distancia_km=None, duracion_min=None):
    """
    puntos: lista de [lat, lng] que siguen la carretera real, calculada en el
    navegador mediante geocoding (Nominatim) + ruteo (OSRM) y enviada ya
    resuelta al servidor para su almacenamiento.
    """
    if len(puntos) < 2:
        raise ValueError("La ruta debe tener al menos dos puntos (origen y destino).")

    if obtener_ruta_por_viaje(id_viaje):
        raise ValueError("Este viaje ya tiene una ruta asignada. Edítala en lugar de crear una nueva.")

    viaje = Viaje.query.get_or_404(id_viaje)

    ruta = Ruta(
        id_viaje=viaje.id_viaje,
        nombre=nombre.strip(),
        origen_texto=(origen_texto or "").strip() or None,
        destino_texto=(destino_texto or "").strip() or None,
        distancia_km=distancia_km,
        duracion_min=duracion_min,
    )
    ruta.puntos = puntos
    db.session.add(ruta)
    db.session.commit()
    return ruta


def actualizar_ruta(id_ruta, nombre, puntos, origen_texto=None, destino_texto=None,
                     distancia_km=None, duracion_min=None):
    if len(puntos) < 2:
        raise ValueError("La ruta debe tener al menos dos puntos (origen y destino).")

    ruta = obtener_ruta(id_ruta)
    ruta.nombre = nombre.strip()
    ruta.puntos = puntos
    ruta.origen_texto = (origen_texto or "").strip() or None
    ruta.destino_texto = (destino_texto or "").strip() or None
    ruta.distancia_km = distancia_km
    ruta.duracion_min = duracion_min
    db.session.commit()
    return ruta


def eliminar_ruta(id_ruta):
    ruta = obtener_ruta(id_ruta)
    db.session.delete(ruta)
    db.session.commit()
