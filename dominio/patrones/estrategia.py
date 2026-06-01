from dominio.puertos import PuertoEstrategia

class Euler(PuertoEstrategia):
    def paso (self, p, dt: float, g:float) -> None:
        # Euler explicito: primero actualiza la velocidad, luego la posicion.
        ax = -p.coef_arrastre / p.masa * p.velocidad() * p.vx # arrastre en x.
        ay = -g - p.coef_arrastre / p.masa * p.velocidad() * p.vy # arrastre en y.

        p.x += p.vx * dt
        p.y += p.vy * dt

        p.vx += ax * dt
        p.vy += ay * dt

    @property
    def nombre(self) -> str: return "Euler (orden 1)"


class Verlet(PuertoEstrategia):
    """Verlet de velocidad - orden 2. Conserva mejor la energia."""
    def paso (self, p, dt: float, g: float) -> None:
        # 1. calcular aceleracion
        ax_actual = -p.coef_arrastre / p.masa * p.velocidad() * p.vx # arrastre en x actual.
        ay_actual = -g - p.coef_arrastre / p.masa * p.velocidad() * p.vy # arrastre en y actual.
        
        # 2. actualizar posicion y velocidad con esa aceleracion
        p.x += p.vx * dt + 0.5 * ax_actual * dt**2
        p.y += p.vy * dt + 0.5 * ay_actual * dt**2

        p.vx += 0.5 * ax_actual * dt
        p.vy += 0.5 * ay_actual * dt 

        # 3. calcular aceleracion en t+dt
        ax_nueva = -p.coef_arrastre / p.masa * p.velocidad() * p.vx
        ay_nueva = -g - p.coef_arrastre / p.masa * p.velocidad() * p.vy

        # 4. actualizar velocidad con el promedio de ambas aceleraciones 

        p.vx += 0.5 * ax_nueva * dt
        p.vy += 0.5 * ay_nueva * dt
        
    @property
    def nombre(self) -> str: return "Verlet para Velocidades (Orden 2)"