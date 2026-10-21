"""Construcción de la solicitud paso a paso con Builder."""
from decimal import Decimal
from .modelos import SolicitudEnvio

class SolicitudBuilder:
    def __init__(self):
        self._datos = {}

    def ruta(self, origen: str, destino: str):
        self._datos.update(origen=origen, destino=destino)
        return self

    def destinatario(self, nombre: str):
        self._datos["destinatario"] = nombre
        return self

    def paquete(self, peso_kg):
        self._datos["peso_kg"] = Decimal(str(peso_kg))
        return self

    def declarar_valor(self, valor):
        self._datos["valor_declarado"] = Decimal(str(valor))
        return self

    def marcar_fragil(self):
        self._datos["fragil"] = True
        return self

    def instrucciones(self, texto: str):
        self._datos["instrucciones"] = texto
        return self

    def referencia(self, texto: str):
        self._datos["referencia"] = texto
        return self

    def construir(self) -> SolicitudEnvio:
        obligatorios = {"origen", "destino", "destinatario", "peso_kg"}
        if not obligatorios.issubset(self._datos):
            raise ValueError("Faltan datos obligatorios de la solicitud")
        return SolicitudEnvio(**self._datos)
