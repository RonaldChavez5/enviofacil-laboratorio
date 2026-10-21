# EnvíoFácil

**Ronald Arturo Chávez Cabrera**  
Ingeniería de Software II (2016702)  
Universidad Nacional de Colombia, Sede Bogotá  
Docente: Sergio Enrique Vargas Pedraza  
21 de octubre de 2026

Para este laboratorio desarrollé un programa de consola que permite cotizar y registrar los envíos de una tienda. Elegí este caso porque reúne varias tareas fáciles de reconocer: calcular el precio, generar una guía, guardar el envío y mostrar un aviso al terminar.

El proyecto corresponde a la **Ruta A**. Las transportadoras y las tarifas son simuladas. Los registros se guardan en memoria y se pierden al cerrar el programa.

[Informe del laboratorio](docs/informe.pdf)

## Cómo ejecutarlo

Se necesita Python 3.10 o posterior. El programa usa la biblioteca estándar y no requiere instalar paquetes adicionales.

Los comandos se ejecutan desde la carpeta que contiene este README y la carpeta `enviofacil`.

Para ver una demostración con dos envíos:

```bash
python -m enviofacil demo
```

Para ingresar los datos y registrar un envío desde la consola:

```bash
python -m enviofacil interactivo
```

Para ejecutar las pruebas:

```bash
python -m unittest discover -s tests -v
```

En Windows también puede usarse `py` en lugar de `python`; en Linux o macOS, `python3`. Si aparece `No module named enviofacil`, hay que revisar que la terminal esté en la carpeta del proyecto.

En el modo interactivo se selecciona `estandar` o `express`, y luego el proveedor `ruta` o `paquete`. El peso se escribe con punto decimal, por ejemplo `1.5`.

La demo utiliza un paquete de 2 kg con un valor declarado de COP 100.000. El resultado esperado es COP 12.000 para el envío estándar y COP 19.000 para el exprés. Después del registro, el programa consulta la guía y muestra el historial y la auditoría. El identificador del envío cambia en cada ejecución.

## Organización del código

Usé un monolito modular y arquitectura hexagonal para separar las reglas del envío de la consola, el almacenamiento y las transportadoras.

| Carpeta o archivo | Contenido |
|---|---|
| `enviofacil/dominio/` | Datos del envío, validaciones, tarifas y guías. |
| `enviofacil/aplicacion/` | Registro, cotización, consulta, interfaces y publicación de avisos. |
| `enviofacil/adaptadores/` | Almacenamiento en memoria, auditoría y transportadoras simuladas. |
| `enviofacil/composicion.py` | Selección de las clases que usa el servicio. |
| `enviofacil/__main__.py` | Entrada del programa por consola. |
| `tests/test_envios.py` | Pruebas del programa. |
| `evidencias/` | Resultados de las pruebas y de las ejecuciones de ejemplo. |
| `docs/` | Informe y diagramas. |

## Patrones utilizados

Las rutas de la siguiente tabla parten de la carpeta `enviofacil`.

| Familia | Patrón | Archivo y clases |
|---|---|---|
| Creacional | Factory Method | `dominio/guias.py`: `CreadorGuia`, `CreadorEstandar`, `CreadorExpress`, `Guia`, `GuiaEstandar` y `GuiaExpress`. |
| Creacional | Builder | `dominio/constructor.py`: `SolicitudBuilder`. El resultado es `SolicitudEnvio`, definido en `dominio/modelos.py`. |
| Estructural | Adapter | `adaptadores/transportadoras.py`: `AdaptadorRutaLocal` y `AdaptadorPaqueteYa`, que implementan `Transportadora`. |
| Estructural | Decorator | `adaptadores/repositorios.py`: `RepositorioAuditado`, que envuelve otro `RepositorioEnvios`, como `RepositorioMemoria`. |
| Comportamiento | Strategy | `dominio/tarifas.py`: `PoliticaTarifa`, `TarifaEstandar` y `TarifaExpress`. `ServicioEnvios` utiliza la tarifa seleccionada. |
| Comportamiento | Observer | `aplicacion/eventos.py`: `PublicadorEnvios`. Los observadores son `HistorialEnvios` y `NotificadorConsola`, en `adaptadores/notificaciones.py`. |

Las interfaces `Transportadora`, `RepositorioEnvios` y `SuscriptorEnvio` están en `aplicacion/puertos.py`. El caso de uso `ServicioEnvios` está en `aplicacion/servicio.py`.

## Pruebas y resultados

Las 22 pruebas terminaron correctamente con Python 3.12.14. Revisan las validaciones, las tarifas, las guías, el almacenamiento y los avisos. También comprueban qué ocurre cuando una transportadora o un observador falla.

Para comprobar el principio abierto/cerrado, la prueba `test_ocp_nueva_estrategia_sin_modificar_servicio` define una tarifa de convenio de COP 9.000 y la utiliza sin cambiar `ServicioEnvios`.

Los resultados completos están en:

- `evidencias/pruebas.txt`
- `evidencias/demo.txt`
- `evidencias/interactivo.txt`

Si falla la transportadora, el envío no se guarda. Si falla un observador después del guardado, el envío se conserva y los demás observadores reciben el aviso. El repositorio rechaza IDs repetidos y conserva los datos de los registros existentes.

## Alcance

El programa permite comprobar el diseño con datos de prueba. No realiza despachos, pagos ni envía mensajes reales. La bitácora guarda la operación y el ID del envío, sin copiar nombres ni direcciones.

Para usarlo en una tienda haría falta almacenamiento permanente, control de acceso e integración con proveedores reales. También habría que manejar los reintentos y el caso en que una transportadora acepte el despacho, pero falle el guardado local.

Los diagramas están en `docs/diagramas/`, en PDF y PNG. Los archivos `.drawio` se pueden abrir y editar con diagrams.net.

## Referencias

- Guía del laboratorio de arquitectura, SOLID y patrones de diseño, Sergio Enrique Vargas Pedraza.
- [Catálogo de patrones de Refactoring.Guru](https://refactoring.guru/es/design-patterns/catalog).
- [Documentación de unittest](https://docs.python.org/3/library/unittest.html).
