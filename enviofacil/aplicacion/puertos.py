"""Interfaces para guardar envíos, solicitar guías y recibir avisos."""
from abc import ABC, abstractmethod
from ..dominio.modelos import Envio, SolicitudEnvio, EnvioRegistrado

class RepositorioEnvios(ABC):
    @abstractmethod
    def guardar(self, envio: Envio) -> None:
        """Guarda un ID nuevo; si existe, lanza ValueError sin sobrescribir."""

    @abstractmethod
    def obtener(self, id_envio: str) -> Envio:
        """Devuelve el envío o lanza KeyError si no existe."""

class Transportadora(ABC):
    @abstractmethod
    def despachar(self, solicitud: SolicitudEnvio) -> str:
        """Devuelve un código de guía no vacío o propaga un error del proveedor."""

class SuscriptorEnvio(ABC):
    @abstractmethod
    def actualizar(self, evento: EnvioRegistrado) -> None:
        pass
