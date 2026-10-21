"""Creación de guías estándar y exprés con Factory Method."""
from abc import ABC, abstractmethod
from .modelos import SolicitudEnvio

class Guia(ABC):
    @abstractmethod
    def texto(self) -> str:
        pass

class GuiaEstandar(Guia):
    def __init__(self, codigo, solicitud):
        self.codigo, self.solicitud = codigo, solicitud

    def texto(self):
        return f"ESTANDAR | {self.codigo} | {self.solicitud.destino}"

class GuiaExpress(Guia):
    def __init__(self, codigo, solicitud):
        self.codigo, self.solicitud = codigo, solicitud

    def texto(self):
        return f"EXPRESS | PRIORIDAD ALTA | {self.codigo} | {self.solicitud.destino}"

class CreadorGuia(ABC):
    def emitir(self, codigo: str, solicitud: SolicitudEnvio) -> str:
        # La operación común usa el producto sin conocer su clase concreta.
        guia = self.crear(codigo, solicitud)
        aviso = " | MANEJAR CON CUIDADO" if solicitud.fragil else ""
        return guia.texto() + aviso

    @abstractmethod
    def crear(self, codigo: str, solicitud: SolicitudEnvio) -> Guia:
        pass

class CreadorEstandar(CreadorGuia):
    def crear(self, codigo, solicitud):
        return GuiaEstandar(codigo, solicitud)

class CreadorExpress(CreadorGuia):
    def crear(self, codigo, solicitud):
        return GuiaExpress(codigo, solicitud)
