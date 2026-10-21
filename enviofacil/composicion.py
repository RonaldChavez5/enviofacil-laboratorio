"""Clases que se utilizan según la modalidad y la transportadora elegidas."""
from .dominio.tarifas import TarifaEstandar, TarifaExpress
from .dominio.guias import CreadorEstandar, CreadorExpress
from .aplicacion.servicio import ServicioEnvios
from .aplicacion.eventos import PublicadorEnvios
from .adaptadores.repositorios import RepositorioMemoria, RepositorioAuditado
from .adaptadores.transportadoras import (ApiRutaLocalSimulada, AdaptadorRutaLocal,
    ApiPaqueteYaSimulada, AdaptadorPaqueteYa)
from .adaptadores.notificaciones import HistorialEnvios, NotificadorConsola

def crear_sistema(modalidad="estandar", proveedor="ruta", notificar=False):
    tarifas = {"estandar": TarifaEstandar, "express": TarifaExpress}
    creadores = {"estandar": CreadorEstandar, "express": CreadorExpress}
    if modalidad not in tarifas or proveedor not in {"ruta", "paquete"}:
        raise ValueError("Modalidad o proveedor no reconocido")
    transportadora = (AdaptadorRutaLocal(ApiRutaLocalSimulada()) if proveedor == "ruta"
                     else AdaptadorPaqueteYa(ApiPaqueteYaSimulada()))
    bitacora, historial, publicador = [], HistorialEnvios(), PublicadorEnvios()
    publicador.suscribir(historial)
    if notificar:
        publicador.suscribir(NotificadorConsola())
    repositorio = RepositorioAuditado(RepositorioMemoria(), bitacora)
    servicio = ServicioEnvios(repositorio, transportadora, tarifas[modalidad](),
                             creadores[modalidad](), publicador)
    return servicio, bitacora, historial
