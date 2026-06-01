#Ensamblador

import sys
from dominio.explosion import Explosion
from dominio.patrones.fabrica import FabricaLigero, FabricaPesado, FabricaConArrastre
from dominio.patrones.estrategia import Euler, Verlet
from dominio.patrones.observador import MonitorEstadisticas

from adaptadores.entrada.cli import EntradaCLI

# Diccionarios para Strategy y Factory Method.
FABRICAS = {
    "ligero"  : FabricaLigero(),
    "pesado"  : FabricaPesado(),
    "arrastre": FabricaConArrastre(),
}
ESTRATEGIAS = {
    "euler" : Euler(),
    "verlet": Verlet(),
}


def _leer_arg(nombre: str, default: str) -> str:
    for i, arg in enumerate(sys.argv):
        if arg == f"--{nombre}" and i + 1 < len(sys.argv):
            return sys.argv[i + 1]
    return default


def main() -> None:
    config = EntradaCLI().obtener_config()

    fabrica    = FABRICAS.get(_leer_arg("tipo", "ligero"), FabricaLigero())
    estrategia = ESTRATEGIAS.get(_leer_arg("metodo", "euler"), Euler())

    monitor      = MonitorEstadisticas()
    observadores = [monitor]

    salida_modo = _leer_arg("salida", "animacion")

    # Solo importar CSV si es necesario.
    if salida_modo in ("csv", "ambos"):
        from adaptadores.salida.csv_output import SalidaCSV
        csv_obs = SalidaCSV("resultados.csv")
        observadores.append(csv_obs)

    # Ejecutar motor.
    print(
        f"[Motor] {config.n_proyectiles} proyectiles | "
        f"fábrica: {fabrica.nombre} | "
        f"integrador: {estrategia.nombre}"
    )
    motor = Explosion(fabrica, estrategia, observadores=observadores)
    trayectorias, resultados = motor.ejecutar(config)

    # Resumen en terminal
    res = monitor.resumen()
    if res:
        print(
            f"Alcance máx: {res['alcance_max']:.1f} m | "
            f"Promedio: {res['promedio']:.1f} m | "
            f"Desviación Estándar: {res['dev_std']:.1f} m"
        )

    # Gráfica.
    if salida_modo in ("animacion", "ambos"):
        from adaptadores.salida.animacion import SalidaAnimacion
        SalidaAnimacion().mostrar(config, trayectorias, resultados)


if __name__ == "__main__":
    main()