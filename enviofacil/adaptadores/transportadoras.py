"""Simulación de dos transportadoras y conversión de sus datos."""
from ..aplicacion.puertos import Transportadora

class ApiRutaLocalSimulada:
    def __init__(self):
        self.ultimo_payload = None
        self._consecutivo = 0

    def crear_orden(self, payload: dict) -> dict:
        self.ultimo_payload = payload
        self._consecutivo += 1
        return {"tracking": f"RL-{self._consecutivo:04d}"}

class AdaptadorRutaLocal(Transportadora):
    def __init__(self, api: ApiRutaLocalSimulada):
        self._api = api

    def despachar(self, solicitud):
        respuesta = self._api.crear_orden({
            "from": solicitud.origen, "to": solicitud.destino,
            "recipient": solicitud.destinatario,
            "grams": int(solicitud.peso_kg * 1000),
            "declared_value": str(solicitud.valor_declarado),
            "fragile": solicitud.fragil, "notes": solicitud.instrucciones,
            "reference": solicitud.referencia,
        })
        return respuesta["tracking"]

class ApiPaqueteYaSimulada:
    def __init__(self):
        self._consecutivo = 0

    def reservar(self, destino: str, kilos: str, contacto: str, extras: dict) -> str:
        self._consecutivo += 1
        return f"PY-{self._consecutivo:04d}"

class AdaptadorPaqueteYa(Transportadora):
    def __init__(self, api: ApiPaqueteYaSimulada):
        self._api = api

    def despachar(self, solicitud):
        return self._api.reservar(solicitud.destino, str(solicitud.peso_kg),
            solicitud.destinatario, {"origen": solicitud.origen,
            "valor": str(solicitud.valor_declarado), "fragil": solicitud.fragil,
            "instrucciones": solicitud.instrucciones, "referencia": solicitud.referencia})
