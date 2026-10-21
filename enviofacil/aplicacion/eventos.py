"""Avisos a los suscriptores después de registrar un envío."""
from .puertos import SuscriptorEnvio
from ..dominio.modelos import EnvioRegistrado

class PublicadorEnvios:
    def __init__(self):
        self._suscriptores: list[SuscriptorEnvio] = []

    def suscribir(self, suscriptor: SuscriptorEnvio):
        if suscriptor not in self._suscriptores:
            self._suscriptores.append(suscriptor)

    def desuscribir(self, suscriptor: SuscriptorEnvio):
        if suscriptor in self._suscriptores:
            self._suscriptores.remove(suscriptor)

    def publicar(self, evento: EnvioRegistrado) -> list[str]:
        errores = []
        for suscriptor in tuple(self._suscriptores):
            try:
                suscriptor.actualizar(evento)
            except Exception as exc:
                errores.append(f"{type(suscriptor).__name__}: {exc}")
        return errores
