"""Datos del envío y validaciones de la solicitud."""
from dataclasses import dataclass
from decimal import Decimal

@dataclass(frozen=True)
class SolicitudEnvio:
    origen: str
    destino: str
    destinatario: str
    peso_kg: Decimal
    valor_declarado: Decimal = Decimal("0")
    fragil: bool = False
    instrucciones: str = ""
    referencia: str = ""

    def __post_init__(self):
        for campo in (self.origen, self.destino, self.destinatario):
            if not isinstance(campo, str) or not campo.strip():
                raise ValueError("Origen, destino y destinatario son obligatorios")
        if not self.peso_kg.is_finite() or self.peso_kg <= 0:
            raise ValueError("El peso debe ser positivo y finito")
        if not self.valor_declarado.is_finite() or self.valor_declarado < 0:
            raise ValueError("El valor declarado no puede ser negativo ni infinito")

@dataclass(frozen=True)
class Envio:
    id: str
    solicitud: SolicitudEnvio
    costo: Decimal
    guia: str

@dataclass(frozen=True)
class EnvioRegistrado:
    envio: Envio
