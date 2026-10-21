"""Opciones para probar el programa y registrar un envío por consola."""
import argparse
from decimal import InvalidOperation
from .composicion import crear_sistema
from .dominio.constructor import SolicitudBuilder

def solicitud_demo():
    return (SolicitudBuilder().ruta("Bogotá", "Tunja").destinatario("Cliente de prueba")
            .paquete("2").declarar_valor("100000").marcar_fragil()
            .instrucciones("Entregar en recepción").referencia("PED-001").construir())

def demo():
    print("ENVÍOFÁCIL | Demo académica | Tarifas y proveedores ficticios")
    solicitud = solicitud_demo()
    for modalidad, proveedor in (("estandar", "ruta"), ("express", "paquete")):
        servicio, bitacora, historial = crear_sistema(modalidad, proveedor, True)
        print(f"\nModalidad: {modalidad}; proveedor: {proveedor}")
        print(f"Cotización: COP {servicio.cotizar(solicitud):,.0f}")
        resultado = servicio.registrar(solicitud)
        recuperado = servicio.consultar(resultado.envio.id)
        print(f"Consulta coincide: {recuperado == resultado.envio}")
        print(f"Historial: {len(historial.ids)} envío; auditoría: {len(bitacora)} operaciones")
        print(f"Avisos de error: {list(resultado.avisos)}")


def interactivo():
    modalidad = input("Modalidad [estandar/express]: ").strip()
    proveedor = input("Proveedor simulado [ruta/paquete]: ").strip()
    servicio, _, _ = crear_sistema(modalidad, proveedor, True)
    builder = SolicitudBuilder().ruta(input("Origen: "), input("Destino: "))
    builder.destinatario(input("Destinatario: ")).paquete(input("Peso en kg: "))
    builder.declarar_valor(input("Valor declarado COP [0]: ").strip() or "0")
    if input("¿Es frágil? [s/n]: ").lower().strip() == "s":
        builder.marcar_fragil()
    builder.instrucciones(input("Instrucciones opcionales: "))
    builder.referencia(input("Referencia opcional: "))
    solicitud = builder.construir()
    print(f"Cotización: COP {servicio.cotizar(solicitud):,.0f}")
    if input("¿Registrar? [s/n]: ").lower().strip() == "s":
        resultado = servicio.registrar(solicitud)
        print(f"ID: {resultado.envio.id}\nGuía: {resultado.envio.guia}")
        print(f"Consulta: {servicio.consultar(resultado.envio.id).guia}")
        for aviso in resultado.avisos:
            print(f"Aviso: {aviso}")


def main():
    parser = argparse.ArgumentParser(description="Gestión académica de envíos")
    parser.add_argument("modo", choices=("demo", "interactivo"), nargs="?", default="demo")
    args = parser.parse_args()
    try:
        demo() if args.modo == "demo" else interactivo()
    except (ValueError, InvalidOperation) as exc:
        parser.exit(2, f"Datos inválidos: {exc}\n")

if __name__ == "__main__":
    main()
