import math
from dominio.modelos import Proyectil
from dominio.puertos import PuertoFabrica

class FabricaLigero(PuertoFabrica):
    def crear(self, angulo_deg: float, v0: float) -> Proyectil:
        ang = math.radians(angulo_deg)
        return Proyectil(x = 0.0, y = 0.0,
                         vx = v0 * math.cos(ang),
                         vy = v0 * math.sin(ang),
                         masa = 0.5, coef_arrastre = 0.0)
    
    @property 
    def nombre(self) -> str: return "Ligero (m = 0.5 kg)"


class FabricaPesado(PuertoFabrica):
    def crear(self, angulo_deg: float, v0: float) -> Proyectil:
        ang = math.radians(angulo_deg)
        return Proyectil(x = 0.0, y = 0.0,
                         vx = v0 * math.cos(ang),
                         vy = v0 * math.sin(ang),
                         masa = 5.0, coef_arrastre = 0.0)
    
    @property 
    def nombre(self) -> str: return "Pesado (m = 5.0 kg)"


class FabricaConArrastre (PuertoFabrica):
    """F_arrastre = coef * v², donde coef = 0.5 *Cd * ρ * A"""
    def __init__(self, cd = 0.47, densidad_aire = 1.225, area = 0.005, masa = 1.0):
        self._coef = 0.5 * cd * densidad_aire * area 
        self._masa = masa


    def crear(self, angulo_deg: float, v0: float) -> Proyectil:
        ang = math.radians(angulo_deg)
        return Proyectil(x = 0.0, y = 0.0,
                         vx = v0 * math.cos(ang),
                         vy = v0 * math.sin(ang),
                         masa = self._masa, 
                         coef_arrastre = self._coef)
    
    @property 
    def nombre(self) -> str: return "Con arrastre (m = 1.0 kg)"