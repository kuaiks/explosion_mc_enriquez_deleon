from dominio.puertos import PuertoObservador
import math


class MonitorEstadisticas(PuertoObservador):
    """Acumula métricas en memoria durante la Simulación."""
    def __init__(self):
        self._alcances: list[float] = []
        self._altura_max: float = 0.0 # altura inicia en 0


    def al_iniciar(self, config) -> None:
        """Reinicia métricas al comenzar la simulación."""
        self._alcances = []
        self._altura_max = 0.0


    def al_finalizar(self, resultados) -> None:
        pass

    def al_aterrizar(self, resultado) -> None:
        self._alcances.append(resultado.alcance)
        if resultado.altura_max > self._altura_max: # va siempre guardando
            self._altura_max = resultado.altura_max
        
    def resumen(self) -> dict: 
        if not self._alcances: #Guard Clause: si _alcances esta vacío, ahorrémonos trabajar con eso.
            return {}
        n = len(self._alcances)
        avg = sum(self._alcances) / n
        std = math.sqrt(sum((x - avg)** 2 for x in self._alcances) / n)
        return {
            "n": n,
            "alcance_max": max(self._alcances),
            "alcance_min": min(self._alcances),
            "promedio": avg,
            "dev_std": std,
            "altura_max": self._altura_max
        }
    
       
        