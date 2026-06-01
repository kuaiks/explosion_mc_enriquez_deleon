import argparse
from dominio.modelos import ConfigExplosion
from dominio.puertos import PuertoEntrada
from adaptadores.entrada.yaml_config import cargar_config_yaml


class EntradaCLI(PuertoEntrada):

    def obtener_config(self) -> ConfigExplosion:
        # leemos el archivo YAML para tener valores por defecto.
        # para que el sistema no se rompa si el usuario no escribe nada agregamos este
        base = cargar_config_yaml("config.yaml")

        # inicializamos argparse para capturar e interpretar lo que el usuario escriba en la consola 

        parser = argparse.ArgumentParser(
            description="Simulación Monte Carlo de una explosión.",
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        )

        # ------ Simulación --------------------------------------------------
        # parametros basicos para controlar el entorno y el bucle fisico.
        parser.add_argument("--n", type=int, default=base.n_proyectiles,
                            help="Numero de proyectiles")
        parser.add_argument("--v-min", type=float, default=base.v_min,
                            help="Velocidad minima (m/s)")
        parser.add_argument("--v-max", type=float, default=base.v_max,
                            help="Velocidad maxima (m/s)")
        parser.add_argument("--g", type=float, default=base.g,
                            help="Gravedad (m/s2). Luna: 1.62")
        parser.add_argument("--dt", type=float, default=base.dt,
                            help="Paso de tiempo (s)")
        parser.add_argument("--semilla", type=int, default=base.semilla,
                            help="Semilla RNG")

        # ------ Patrones --------------------------------------------------
        # estos definen "que" clases se van a instanciar más adelante.
        parser.add_argument("--tipo",
                            choices=["ligero", "pesado", "arrastre"],
                            default="ligero",
                            help="Tipo de proyectil (fabrica)")
        parser.add_argument("--metodo",
                            choices=["euler", "verlet"],
                            default="euler",
                            help="Integrador numérico (estrategia)")

        # ------ Salida --------------------------------------------------
        # para ver la simulación visual o guardar datos crudos.
        parser.add_argument("--salida",
                            choices=["animacion", "csv", "ambos"],
                            default="animacion",
                            help="Modo de salida")

        # ------ Distribución de ángulos --------------------------------------------------
        # Controla hacia dónde salen disparados
        parser.add_argument("--dist-angulo",
                            choices=["uniforme", "normal", "vonmises"],
                            default=base.dist_angulo,
                            help="Distribución de ángulos")
        parser.add_argument("--angulo-media", type=float, default=base.angulo_media,
                            help="Media del ángulo en grados (normal/vonmises)")
        parser.add_argument("--angulo-sigma", type=float, default=base.angulo_sigma,
                            help="Desviación estándar del ángulo (normal)")
        parser.add_argument("--angulo-kappa", type=float, default=base.angulo_kappa,
                            help="Concentración de vonmises")

        # ------ Distribución de velocidades --------------------------------------------------
        # aleatoriza la energia/fuerza inicial
        parser.add_argument("--dist-vel",
                            choices=["uniforme", "normal", "exponencial"],
                            default=base.dist_velocidad,
                            help="Distribucion de velocidades iniciales")
        parser.add_argument("--vel-media", type=float, default=base.vel_media,
                            help="Media de velocidad m/s")
        parser.add_argument("--vel-sigma", type=float, default=base.vel_sigma,
                            help="Desviación estándar de velocidad")

        args = parser.parse_args()

        #construir ConfigExplosion con los valores finales
        return ConfigExplosion(
            n_proyectiles  = args.n,
            v_min          = args.v_min,
            v_max          = args.v_max,
            g              = args.g,
            dt             = args.dt,
            semilla        = args.semilla,
            trail_length   = base.trail_length,
            modo_ejecucion = base.modo_ejecucion,
            workers        = base.workers,
            dist_angulo    = args.dist_angulo,
            angulo_media   = args.angulo_media,
            angulo_sigma   = args.angulo_sigma,
            angulo_kappa   = args.angulo_kappa,
            dist_velocidad = args.dist_vel,
            vel_media      = args.vel_media,
            vel_sigma      = args.vel_sigma,
        )
