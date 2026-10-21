"""Cálculo de las tarifas de ejemplo en pesos colombianos."""
from abc import ABC, abstractmethod
from decimal import Decimal
from .modelos import SolicitudEnvio

class PoliticaTarifa(ABC):
    @abstractmethod
    def calcular(self, solicitud: SolicitudEnvio) -> Decimal:
        """Devuelve un costo finito no negativo; no modifica la solicitud."""

class TarifaEstandar(PoliticaTarifa):
    def calcular(self, solicitud):
        return (Decimal("7000") + Decimal("2000") * solicitud.peso_kg
                + Decimal("0.01") * solicitud.valor_declarado).quantize(Decimal("1"))

class TarifaExpress(PoliticaTarifa):
    def calcular(self, solicitud):
        return (Decimal("12000") + Decimal("3000") * solicitud.peso_kg
                + Decimal("0.01") * solicitud.valor_declarado).quantize(Decimal("1"))
