"""Operaciones para cotizar, registrar y consultar envíos."""
from dataclasses import dataclass
from decimal import Decimal
from uuid import uuid4
from ..dominio.modelos import Envio, EnvioRegistrado, SolicitudEnvio
from ..dominio.tarifas import PoliticaTarifa
from ..dominio.guias import CreadorGuia
from .puertos import RepositorioEnvios, Transportadora
from .eventos import PublicadorEnvios

@dataclass(frozen=True)
class ResultadoRegistro:
    envio: Envio
    avisos: tuple[str, ...]

class ServicioEnvios:
    def __init__(self, repositorio: RepositorioEnvios, transportadora: Transportadora,
                 tarifa: PoliticaTarifa, creador: CreadorGuia, publicador: PublicadorEnvios):
        self._repositorio = repositorio
        self._transportadora = transportadora
        self._tarifa = tarifa
        self._creador = creador
        self._publicador = publicador

    def cotizar(self, solicitud: SolicitudEnvio) -> Decimal:
        costo = self._tarifa.calcular(solicitud)
        if not costo.is_finite() or costo < 0:
            raise ValueError("La tarifa debe devolver un costo finito no negativo")
        return costo

    def registrar(self, solicitud: SolicitudEnvio) -> ResultadoRegistro:
        costo = self.cotizar(solicitud)
        codigo = self._transportadora.despachar(solicitud)
        if not codigo.strip():
            raise ValueError("La transportadora no devolvió un código de guía")
        guia = self._creador.emitir(codigo, solicitud)
        envio = Envio(str(uuid4()), solicitud, costo, guia)
        self._repositorio.guardar(envio)
        avisos = self._publicador.publicar(EnvioRegistrado(envio))
        return ResultadoRegistro(envio, tuple(avisos))

    def consultar(self, id_envio: str) -> Envio:
        return self._repositorio.obtener(id_envio)
