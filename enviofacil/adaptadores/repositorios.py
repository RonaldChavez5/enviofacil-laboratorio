"""Guardado en memoria y registro de operaciones en la bitácora."""
from ..aplicacion.puertos import RepositorioEnvios

class RepositorioMemoria(RepositorioEnvios):
    def __init__(self):
        self._envios = {}

    def guardar(self, envio):
        if envio.id in self._envios:
            raise ValueError("El ID ya existe")
        self._envios[envio.id] = envio

    def obtener(self, id_envio):
        return self._envios[id_envio]

class RepositorioAuditado(RepositorioEnvios):
    def __init__(self, interno: RepositorioEnvios, bitacora: list[str]):
        self._interno = interno
        self._bitacora = bitacora

    def guardar(self, envio):
        self._interno.guardar(envio)
        self._bitacora.append(f"GUARDAR {envio.id}")

    def obtener(self, id_envio):
        envio = self._interno.obtener(id_envio)
        self._bitacora.append(f"CONSULTAR {id_envio}")
        return envio
