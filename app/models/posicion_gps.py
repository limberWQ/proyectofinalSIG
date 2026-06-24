from datetime import datetime
from app import db


class PosicionGps(db.Model):
    """
    Última posición real reportada por el dispositivo móvil vinculado a un viaje.
    Se sobrescribe en cada actualización (no se guarda historial), ya que solo
    interesa la posición actual del bus para el panel de monitoreo.
    """
    __tablename__ = "posicion_gps"

    id_posicion = db.Column(db.Integer, primary_key=True, autoincrement=True)
    id_viaje = db.Column(db.Integer, db.ForeignKey("viaje.id_viaje"), nullable=False, unique=True)
    latitud = db.Column(db.Float, nullable=False)
    longitud = db.Column(db.Float, nullable=False)
    precision_metros = db.Column(db.Float, nullable=True)
    actualizado_en = db.Column(db.DateTime, nullable=False, default=datetime.now)

    viaje = db.relationship("Viaje", backref=db.backref("posicion_gps", uselist=False, cascade="all, delete-orphan"))

    def __repr__(self):
        return f"<PosicionGps viaje={self.id_viaje} ({self.latitud}, {self.longitud})>"
