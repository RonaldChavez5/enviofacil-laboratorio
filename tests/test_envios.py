import unittest
from dataclasses import FrozenInstanceError
from decimal import Decimal
from enviofacil.dominio.constructor import SolicitudBuilder
from enviofacil.dominio.modelos import Envio, EnvioRegistrado
from enviofacil.dominio.tarifas import PoliticaTarifa, TarifaEstandar, TarifaExpress
from enviofacil.dominio.guias import CreadorEstandar, CreadorExpress
from enviofacil.aplicacion.puertos import Transportadora, SuscriptorEnvio
from enviofacil.aplicacion.eventos import PublicadorEnvios
from enviofacil.aplicacion.servicio import ServicioEnvios
from enviofacil.adaptadores.repositorios import RepositorioMemoria, RepositorioAuditado
from enviofacil.adaptadores.transportadoras import (
    ApiRutaLocalSimulada, AdaptadorRutaLocal, ApiPaqueteYaSimulada, AdaptadorPaqueteYa)
from enviofacil.adaptadores.notificaciones import HistorialEnvios
from enviofacil.composicion import crear_sistema


def solicitud(peso="2", valor="100000"):
    return (SolicitudBuilder().ruta("Bogotá", "Tunja").destinatario("Persona de prueba")
            .paquete(peso).declarar_valor(valor).construir())


def servicio_con(tarifa=None, transportadora=None, repositorio=None, publicador=None):
    return ServicioEnvios(repositorio or RepositorioMemoria(),
        transportadora or AdaptadorRutaLocal(ApiRutaLocalSimulada()),
        tarifa or TarifaEstandar(), CreadorEstandar(), publicador or PublicadorEnvios())


class TestDominio(unittest.TestCase):
    def test_builder_campos_opcionales(self):
        pedido = (SolicitudBuilder().ruta("A", "B").destinatario("C").paquete("1.5")
                  .marcar_fragil().instrucciones("Portería").referencia("P-1").construir())
        self.assertTrue(pedido.fragil)
        self.assertEqual(pedido.instrucciones, "Portería")
        self.assertEqual(pedido.referencia, "P-1")
        self.assertEqual(pedido.valor_declarado, 0)

    def test_builder_rechaza_datos_incompletos(self):
        with self.assertRaises(ValueError):
            SolicitudBuilder().paquete("2").construir()

    def test_valida_peso_y_valor(self):
        for peso in ("0", "-1", "NaN", "Infinity"):
            with self.subTest(peso=peso), self.assertRaises(ValueError):
                solicitud(peso)
        for valor in ("-1", "NaN", "Infinity"):
            with self.subTest(valor=valor), self.assertRaises(ValueError):
                solicitud(valor=valor)

    def test_rechaza_destinatario_vacio(self):
        with self.assertRaises(ValueError):
            SolicitudBuilder().ruta("A", "B").destinatario(" ").paquete(1).construir()

    def test_producto_inmutable_e_independiente_del_builder(self):
        builder = SolicitudBuilder().ruta("A", "B").destinatario("C").paquete(1)
        primero = builder.construir()
        builder.paquete(2)
        self.assertEqual(primero.peso_kg, 1)
        self.assertEqual(builder.construir().peso_kg, 2)
        with self.assertRaises(FrozenInstanceError):
            primero.destino = "D"

    def test_tarifas_con_valores_esperados(self):
        self.assertEqual(TarifaEstandar().calcular(solicitud()), Decimal("12000"))
        self.assertEqual(TarifaExpress().calcular(solicitud()), Decimal("19000"))

    def test_factory_method_productos_distintos(self):
        pedido = solicitud()
        self.assertEqual(CreadorEstandar().emitir("X", pedido), "ESTANDAR | X | Tunja")
        self.assertEqual(CreadorExpress().emitir("X", pedido),
                         "EXPRESS | PRIORIDAD ALTA | X | Tunja")

    def test_factory_conserva_aviso_fragil(self):
        pedido = (SolicitudBuilder().ruta("A", "B").destinatario("C")
                  .paquete(1).marcar_fragil().construir())
        for creador in (CreadorEstandar(), CreadorExpress()):
            with self.subTest(creador=type(creador).__name__):
                self.assertIn("MANEJAR CON CUIDADO", creador.emitir("X", pedido))


class TestContratos(unittest.TestCase):
    def test_liskov_repositorios_guardar_consultar_y_errores(self):
        for repo in (RepositorioMemoria(), RepositorioAuditado(RepositorioMemoria(), [])):
            with self.subTest(repo=type(repo).__name__):
                envio = Envio("1", solicitud(), Decimal("12000"), "G1")
                with self.assertRaises(KeyError):
                    repo.obtener("ausente")
                repo.guardar(envio)
                self.assertEqual(repo.obtener("1"), envio)
                with self.assertRaises(ValueError):
                    repo.guardar(Envio("1", solicitud(), Decimal("0"), "otro"))
                self.assertEqual(repo.obtener("1"), envio)

    def test_decorator_audita_solo_operaciones_exitosas(self):
        log = []
        repo = RepositorioAuditado(RepositorioMemoria(), log)
        envio = Envio("1", solicitud(), Decimal("12000"), "G1")
        repo.guardar(envio)
        repo.obtener("1")
        with self.assertRaises(KeyError):
            repo.obtener("inexistente")
        self.assertEqual(log, ["GUARDAR 1", "CONSULTAR 1"])

    def test_adapter_traduce_payload_y_respuesta(self):
        api = ApiRutaLocalSimulada()
        codigo = AdaptadorRutaLocal(api).despachar(solicitud("1.5"))
        self.assertEqual(codigo, "RL-0001")
        self.assertEqual(api.ultimo_payload["grams"], 1500)
        self.assertEqual(api.ultimo_payload["to"], "Tunja")
        self.assertEqual(api.ultimo_payload["declared_value"], "100000")

    def test_liskov_transportadoras_intercambiables(self):
        proveedores = (AdaptadorRutaLocal(ApiRutaLocalSimulada()),
                       AdaptadorPaqueteYa(ApiPaqueteYaSimulada()))
        for proveedor in proveedores:
            with self.subTest(proveedor=type(proveedor).__name__):
                resultado = servicio_con(transportadora=proveedor).registrar(solicitud())
                self.assertTrue(resultado.envio.guia)
                self.assertEqual(resultado.envio.costo, Decimal("12000"))

    def test_codigos_diferentes_en_misma_api(self):
        proveedor = AdaptadorRutaLocal(ApiRutaLocalSimulada())
        self.assertNotEqual(proveedor.despachar(solicitud()), proveedor.despachar(solicitud()))


class TestCasosDeUso(unittest.TestCase):
    def test_registro_consulta_auditoria_e_historial(self):
        servicio, log, historial = crear_sistema()
        resultado = servicio.registrar(solicitud())
        self.assertEqual(servicio.consultar(resultado.envio.id), resultado.envio)
        self.assertEqual(historial.ids, [resultado.envio.id])
        self.assertEqual(len(log), 2)
        self.assertEqual(resultado.avisos, ())

    def test_cotizar_no_registra_ni_publica(self):
        servicio, log, historial = crear_sistema()
        self.assertEqual(servicio.cotizar(solicitud()), Decimal("12000"))
        self.assertEqual(log, [])
        self.assertEqual(historial.ids, [])

    def test_ocp_nueva_estrategia_sin_modificar_servicio(self):
        # Extensión definida fuera del módulo productivo de tarifas.
        class TarifaConvenio(PoliticaTarifa):
            def calcular(self, pedido):
                return Decimal("9000")
        servicio = servicio_con(tarifa=TarifaConvenio())
        self.assertEqual(servicio.cotizar(solicitud()), Decimal("9000"))
        self.assertEqual(servicio.registrar(solicitud()).envio.costo, Decimal("9000"))

    def test_rechaza_tarifa_fuera_de_contrato(self):
        class TarifaInvalida(PoliticaTarifa):
            def calcular(self, pedido):
                return Decimal("-1")
        with self.assertRaises(ValueError):
            servicio_con(tarifa=TarifaInvalida()).registrar(solicitud())

    def test_falla_proveedor_no_guarda_ni_publica(self):
        class ProveedorCaido(Transportadora):
            def despachar(self, pedido):
                raise RuntimeError("Proveedor no disponible")
        log, historial = [], HistorialEnvios()
        publicador = PublicadorEnvios()
        publicador.suscribir(historial)
        repo = RepositorioAuditado(RepositorioMemoria(), log)
        servicio = servicio_con(transportadora=ProveedorCaido(), repositorio=repo,
                                publicador=publicador)
        with self.assertRaises(RuntimeError):
            servicio.registrar(solicitud())
        self.assertEqual(log, [])
        self.assertEqual(historial.ids, [])

    def test_rechaza_codigo_vacio(self):
        class SinCodigo(Transportadora):
            def despachar(self, pedido):
                return " "
        with self.assertRaises(ValueError):
            servicio_con(transportadora=SinCodigo()).registrar(solicitud())


class TestObserver(unittest.TestCase):
    def test_varios_suscriptores_sin_duplicados(self):
        pub, uno, dos = PublicadorEnvios(), HistorialEnvios(), HistorialEnvios()
        pub.suscribir(uno)
        pub.suscribir(uno)
        pub.suscribir(dos)
        evento = EnvioRegistrado(Envio("1", solicitud(), Decimal("12000"), "G1"))
        self.assertEqual(pub.publicar(evento), [])
        self.assertEqual(uno.ids, ["1"])
        self.assertEqual(dos.ids, ["1"])

    def test_desuscripcion(self):
        pub, historial = PublicadorEnvios(), HistorialEnvios()
        pub.suscribir(historial)
        pub.desuscribir(historial)
        pub.publicar(EnvioRegistrado(Envio("1", solicitud(), Decimal("12000"), "G1")))
        self.assertEqual(historial.ids, [])

    def test_error_observador_no_revierte_registro_ni_bloquea_otros(self):
        class ObservadorFallido(SuscriptorEnvio):
            def actualizar(self, evento):
                raise RuntimeError("Canal no disponible")
        pub, historial = PublicadorEnvios(), HistorialEnvios()
        pub.suscribir(ObservadorFallido())
        pub.suscribir(historial)
        servicio = servicio_con(publicador=pub)
        resultado = servicio.registrar(solicitud())
        self.assertEqual(servicio.consultar(resultado.envio.id), resultado.envio)
        self.assertEqual(historial.ids, [resultado.envio.id])
        self.assertIn("Canal no disponible", resultado.avisos[0])

if __name__ == "__main__":
    unittest.main()
