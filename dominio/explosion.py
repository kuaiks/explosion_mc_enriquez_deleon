import math
import random
from dominio.modelos import ConfigExplosion, ResultadoProyectil, Proyectil
from dominio.puertos import PuertoFabrica, PuertoEstrategia, PuertoObservador

class Explosion:
    def __init__(self, fabrica: PuertoFabrica,
                 estrategia: PuertoEstrategia,
                 observadores: list[PuertoObservador] | None = None):
        self._fabrica = fabrica
        self._estrategia = estrategia
        self._observadores = list(observadores or [])

    def _calcular_alcance(self, trayectoria: list) -> float:
        """Calcula el alcance interpolando linealmente al cruzar el suelo."""
        for i in range(len(trayectoria) - 1):
            x1, y1 = trayectoria[i]
            x2, y2 = trayectoria[i + 1]
            if y2 < 0:
                # Aquí es la interpolación lineal cuando cruza y = 0.
                f = y1 / (y1 - y2)
                alcance = x1 + f * (x2 - x1)
                return max(0.0, alcance)
        return trayectoria[-1][0] if trayectoria else 0.0
    

    def _simular_un_proyectil(self, p: Proyectil, config: ConfigExplosion, angulo_deg: float, v0: float) -> tuple[list, ResultadoProyectil]:
        """Simula un proyectil desde el origen hasta que toca el suelo."""
        trayectoria = [(p.x, p.y)]
        t = 0.0
        energia_inicial = p.energia_total(config.g)


        while p.y >= 0 and t < 30.0: #t_max = 30s
            self._estrategia.paso(p, config.dt, config.g)
            trayectoria.append((p.x, p.y))
            t += config.dt

        
        alcance = self._calcular_alcance(trayectoria)
        altura_max = max(y for _, y in trayectoria)
        energia_final = p.energia_total(config.g)

        resultado = ResultadoProyectil(
            angulo_deg = angulo_deg,
            v0 = v0,
            masa = p.masa,
            alcance = alcance,
            altura_max = altura_max,
            tiempo_vuelo = t, 
            energia_inicial = energia_inicial,
            energia_final = energia_final,
            trayectoria = trayectoria
        )

        return trayectoria, resultado



    def _generar_angulo(self, rng, config: ConfigExplosion) -> float:
        """Generar un ángulo según la distribución dada."""
        if config.dist_angulo == "uniforme":
            return rng.uniform(0.0, 360.0)
        elif config.dist_angulo == "normal":
            angulo = rng.gauss(config.angulo_media, config.angulo_sigma)
            return angulo % 360.0
        elif config.dist_angulo == "vonmises":
            angulo_rad = rng.vonmisesvariate(math.radians(config.angulo_media), config.angulo_kappa)
            return math.degrees(angulo_rad) % 360.0
        else:
            return rng.uniform(0.0, 360.0)
    


    def _generar_velocidad(self, rng, config: ConfigExplosion) -> float:
        """Generar una velocidad según la distribución dada."""
        if config.dist_velocidad == "uniforme":
            return rng.uniform(config.v_min, config.v_max)
        elif config.dist_velocidad == "normal":
            return rng.uniform(config.vel_media, config.vel_sigma)
        elif config.dist_velocidad == "exponencial":
            return rng.expovariate(1.0 / config.vel_media)
        else:
            return rng.uniform(config.v_min, config.v_max)


    def ejecutar(self, config: ConfigExplosion) -> tuple[list, list]:
        """Simula la explosión completa. Devuelve (trayectorias, resultados)."""
        rng = random.Random(config.semilla)
        trayectorias = []
        resultados = []

        # Notificar el inicio a los observadores.
        for obs in self._observadores:
            obs.al_iniciar(config)

        for i in range(config.n_proyectiles):
            # Genera ángulo y velocidad.
            angulo = self._generar_angulo(rng, config)
            v0 = self._generar_velocidad(rng, config)

            # Crear proyectil.
            p = self._fabrica.crear(angulo, v0)

            # Simular.
            tray, resultado = self._simular_un_proyectil(p, config, angulo, v0)
            trayectorias.append(tray)   
            resultados.append(resultado)

            # Notificar aterrizaje a los observadores.

            for obs in self._observadores:
                obs.al_aterrizar(resultado)
        
        # Notificar final a los observadores.
        for obs in self._observadores:
            obs.al_finalizar(resultados)
        
        return trayectorias, resultados
