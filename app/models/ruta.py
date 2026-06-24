import json
from app import db


class Ruta(db.Model):
    """
    Ruta geográfica asociada a un viaje. Los puntos se guardan como GeoJSON
    (lista de [lat, lng]) en un campo de texto. La ruta se calcula automáticamente
    siguiendo calles reales (vía OSRM) a partir del origen/destino geocodificados
    (vía Nominatim), por lo que contiene muchos puntos intermedios (la "polilínea"
    real de la carretera), no solo origen y destino.
    """
    __tablename__ = "ruta"

    id_ruta = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_viaje = db.Column(db.Integer, db.ForeignKey("viaje.id_viaje"), nullable=False, unique=True)
    nombre = db.Column(db.String(150), nullable=False)
    puntos_geojson = db.Column(db.Text, nullable=False)  # '[[lat,lng],[lat,lng],...]' siguiendo la carretera

    origen_texto = db.Column(db.String(150), nullable=True)
    destino_texto = db.Column(db.String(150), nullable=True)
    distancia_km = db.Column(db.Float, nullable=True)
    duracion_min = db.Column(db.Float, nullable=True)

    viaje = db.relationship("Viaje", backref=db.backref("ruta", uselist=False, cascade="all, delete-orphan"))

    @property
    def puntos(self):
        try:
            return json.loads(self.puntos_geojson)
        except (TypeError, ValueError):
            return []

    @puntos.setter
    def puntos(self, lista_puntos):
        self.puntos_geojson = json.dumps(lista_puntos)

    def __repr__(self):
        return f"<Ruta {self.nombre} (viaje {self.id_viaje})>"
