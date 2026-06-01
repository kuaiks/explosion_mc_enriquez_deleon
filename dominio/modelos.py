from dataclasses import dataclass, field
import math

@dataclass
class Proyectil:
    x: float; y: float; vx: float; vy: float
    masa: float = 1.0
    coef_arrastre : float = 0.0

    def velocidad(self) -> float: 
        return math.hypot(self.vx, self.vy)
    
    def energia_cinetica(self) -> float: 
        return 0.5 * self.masa * self.velocidad()**2
    
    def energia_potencial(self, g: float = 9.8) -> float: 
        return self.masa * g * self.y
    
    def energia_total(self, g: float = 9.8) -> float: 
        return self.energia_cinetica() + self.energia_potencial(g)

@dataclass
class ResultadoProyectil:
    angulo_deg: float; v0: float; masa: float
    alcance: float; altura_max: float; tiempo_vuelo: float
    energia_inicial: float; energia_final: float
    trayectoria: list = field(default_factory=list) # que es esto xD
    
    @property # esto tampoco sé qué es xD. Creo que es el error de calculo no me recuerdo como se llama xd
    def error_energia(self) -> float:
        """Variacion relativa de energia: |E_final - E_inicial| / |E_inicial|"""
        if self.energia_inicial == 0:
            return 0.0
        return abs(self.energia_final - self.energia_inicial) / abs(self.energia_inicial)

@dataclass
class ConfigExplosion:
    n_proyectiles: int = 300
    v_min: float = 5.0
    v_max: float = 30.0
    g: float = 9.8
    dt: float = 0.04
    semilla: int = 42
    trail_length: int = 18
    modo_ejecucion: str = "secuencial"
    workers: int | None = None
    dist_angulo: str = "uniforme"
    angulo_media: float = 90.0
    angulo_sigma: float = 20.0
    angulo_kappa: float = 6.0
    dist_velocidad: str = "uniforme"
    vel_media: float = 12.0
    vel_sigma: float = 4.0

    

