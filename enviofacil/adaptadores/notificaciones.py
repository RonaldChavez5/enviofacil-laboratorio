"""Aviso por consola e historial de los envíos registrados."""
from ..aplicacion.puertos import SuscriptorEnvio

class NotificadorConsola(SuscriptorEnvio):
    def actualizar(self, evento):
        print(f"AVISO: envío {evento.envio.id} registrado; guía: {evento.envio.guia}")

class HistorialEnvios(SuscriptorEnvio):
    def __init__(self):
        self.ids = []

    def actualizar(self, evento):
        self.ids.append(evento.envio.id)
