import pytest
import math
from dominio.modelos import Proyectil, ConfigExplosion, ResultadoProyectil
from dominio.patrones.fabrica import FabricaLigero, FabricaPesado, FabricaConArrastre
from dominio.patrones.estrategia import Euler, Verlet
from dominio.patrones.observador import MonitorEstadisticas
from dominio.explosion import Explosion
from dominio.puertos import PuertoObservador

# Todos los fixtures.

@pytest.fixture
def config_minima():
    return ConfigExplosion(
        n_proyectiles=20,
        v_min=10.0,
        v_max=20.0,
        semilla=42,
        g=9.8,
        dt=0.04
    )

@pytest.fixture
def config_angulos_360():
    return ConfigExplosion(
        n_proyectiles=100,
        v_min=10.0,
        v_max=20.0,
        semilla=123,
        dist_angulo="uniforme"
    )

@pytest.fixture
def motor_euler():
    monitor = MonitorEstadisticas()
    motor = Explosion(FabricaLigero(), Euler(), [monitor])
    return motor, monitor

@pytest.fixture
def motor_verlet():
    monitor = MonitorEstadisticas()
    motor = Explosion(FabricaLigero(), Verlet(), [monitor])
    return motor, monitor

@pytest.fixture
def proyectil_ejemplo():
    return Proyectil(x=0.0, y=0.0, vx=10.0, vy=10.0, masa=1.0, coef_arrastre=0.0)



# Tests de los Modelos.

class TestProyectil:
    def test_velocidad_correcta(self, proyectil_ejemplo):
        assert proyectil_ejemplo.velocidad() == math.sqrt(10**2 + 10**2)
    
    def test_energia_cinetica_correcta(self, proyectil_ejemplo):
        # Ec = 0.5 * m * v² = 0.5 * 1 * (√200)² = 100
        assert proyectil_ejemplo.energia_cinetica() == pytest.approx(100.0)
    
    def test_energia_potencial_correcta(self, proyectil_ejemplo):
        proyectil_ejemplo.y = 5.0
        # Ep = m * g * h = 1 * 9.8 * 5 = 49
        assert proyectil_ejemplo.energia_potencial(9.8) == 49.0
    
    def test_energia_total_correcta(self, proyectil_ejemplo):
        proyectil_ejemplo.y = 5.0
        # Et = Ec + Ep = 100 + 49 = 149
        assert proyectil_ejemplo.energia_total(9.8) == 149.0

class TestResultadoProyectil:
    def test_error_energia_calculo_correcto(self):
        resultado = ResultadoProyectil(
            angulo_deg=45.0, v0=20.0, masa=1.0,
            alcance=40.0, altura_max=10.0, tiempo_vuelo=2.0,
            energia_inicial=200.0, energia_final=190.0,
            trayectoria=[]
        )
        # |190 - 200| / 200 = 10 / 200 = 0.05
        assert resultado.error_energia == 0.05
    
    def test_error_energia_con_energia_inicial_cero(self):
        resultado = ResultadoProyectil(
            angulo_deg=0.0, v0=0.0, masa=1.0,
            alcance=0.0, altura_max=0.0, tiempo_vuelo=0.0,
            energia_inicial=0.0, energia_final=0.0,
            trayectoria=[]
        )
        assert resultado.error_energia == 0.0

# Tests de las fábricas.

class TestFabricas:
    def test_fabrica_ligero_crea_proyectil_correcto(self):
        p = FabricaLigero().crear(45, 20)
        assert isinstance(p, Proyectil)
        assert p.masa == 0.5
        assert p.coef_arrastre == 0.0
    
    def test_fabrica_pesado_crea_proyectil_correcto(self):
        p = FabricaPesado().crear(45, 20)
        assert p.masa == 5.0
        assert p.coef_arrastre == 0.0
    
    def test_fabrica_con_arrastre_crea_proyectil_correcto(self):
        p = FabricaConArrastre().crear(45, 20)
        assert p.masa == 1.0
        assert p.coef_arrastre > 0  # Debería tener arrastre.
    
    def test_velocidad_inicial_correcta(self):
        p = FabricaLigero().crear(45, 20.0)
        v = math.sqrt(p.vx**2 + p.vy**2)
        assert abs(v - 20.0) < 1e-9
    
    def test_sin_if_en_fabrica_ligero_crear(self):
        """FabricaLigero.crear no debe tener ningún if/elif"""
        import inspect, ast, textwrap
        src = textwrap.dedent(inspect.getsource(FabricaLigero.crear))
        ifs = [n for n in ast.walk(ast.parse(src)) if isinstance(n, ast.If)]
        assert len(ifs) == 0




# Tests de estrategias.

class TestEstrategias:
    @pytest.mark.parametrize("angulo_deg", [30, 45, 60, 75])
    def test_alcance_vs_analitico_euler(self, angulo_deg):
        """Sin arrastre con Euler: error < 5% con dt=0.002"""
        v0, g = 20.0, 9.8
        p = FabricaLigero().crear(angulo_deg, v0)
        euler = Euler()
        
        while True:
            x_prev, y_prev = p.x, p.y
            euler.paso(p, 0.002, g)
            if p.y < 0 and p.x != 0:
                f = y_prev / (y_prev - p.y)
                x_imp = x_prev + f * (p.x - x_prev)
                break
        
        R_teorico = v0 ** 2 * math.sin(2 * math.radians(angulo_deg)) / g
        error = abs(x_imp - R_teorico) / R_teorico
        assert error < 0.05  # 5% de error .
    
    def test_verlet_conserva_mejor_energia_que_euler(self):
        def error_energia(estrategia):
            p = FabricaLigero().crear(45, 20)
            e0 = p.energia_total(9.8)
            for _ in range(500):
                estrategia.paso(p, 0.05, 9.8)
                if p.y < 0:
                    break
            if p.energia_total(9.8) == 0:
                return float('inf')
            return abs(p.energia_total(9.8) - e0) / abs(e0)
        
        error_verlet = error_energia(Verlet())
        error_euler = error_energia(Euler())
        assert error_verlet < error_euler


# Tests de los Observadores.

class TestMonitorEstadisticas:
    def test_monitor_recibe_todos_los_aterrizajes(self, config_minima, motor_euler):
        motor, monitor = motor_euler
        motor.ejecutar(config_minima)
        assert monitor.resumen()["n"] == config_minima.n_proyectiles
    
    def test_resumen_tiene_claves_esperadas(self, config_minima, motor_euler):
        motor, monitor = motor_euler
        motor.ejecutar(config_minima)
        for clave in ("n", "alcance_max", "alcance_min", "promedio", "dev_std", "altura_max"):
            assert clave in monitor.resumen()
    
    def test_monitor_se_reinicia_al_iniciar(self):
        monitor = MonitorEstadisticas()
        # Simular algunos aterrizajes.
        resultado = ResultadoProyectil(45, 20, 1, 50, 10, 2, 100, 95, [])
        monitor.al_aterrizar(resultado)
        monitor.al_aterrizar(resultado)
        assert monitor.resumen()["n"] == 2
        
        # El reinicio.
        monitor.al_iniciar(None)
        assert monitor.resumen() == {}  # Sin nada luego de reiniciar.



# Tests de explosiones.

class TestExplosion:
    def test_trayectorias_empiezan_en_origen(self, config_minima):
        motor = Explosion(FabricaLigero(), Euler())
        trayectorias, _ = motor.ejecutar(config_minima)
        for tray in trayectorias:
            assert tray[0] == (0.0, 0.0)
    
    def test_reproducibilidad_con_misma_semilla(self):
        config = ConfigExplosion(n_proyectiles=30, semilla=99, v_min=10, v_max=20)
        _, r1 = Explosion(FabricaLigero(), Euler()).ejecutar(config)
        _, r2 = Explosion(FabricaLigero(), Euler()).ejecutar(config)
        for a, b in zip(r1, r2):
            assert abs(a.alcance - b.alcance) < 1e-10
    
    def test_angulos_en_rango_0_360(self, config_angulos_360):
        motor = Explosion(FabricaLigero(), Euler())
        _, resultados = motor.ejecutar(config_angulos_360)
        
        for resultado in resultados:
            assert 0 <= resultado.angulo_deg <= 360
    
    def test_velocidades_en_rango_v_min_v_max(self, config_minima):
        motor = Explosion(FabricaLigero(), Euler())
        _, resultados = motor.ejecutar(config_minima)
        
        for resultado in resultados:
            assert config_minima.v_min <= resultado.v0 <= config_minima.v_max
    
    def test_nuevo_observador_sin_modificar_motor(self):
        """Agregar un observador personalizado no debe requerir cambiar Explosion."""
        eventos = []
        
        class ObsCustom(PuertoObservador):
            def al_iniciar(self, config):
                eventos.append("inicio")
            def al_aterrizar(self, r):
                eventos.append(r.alcance)
            def al_finalizar(self, resultados):
                eventos.append("fin")
        
        config = ConfigExplosion(n_proyectiles=10, v_min=10, v_max=20, semilla=1)
        motor = Explosion(FabricaLigero(), Euler(), [ObsCustom()])
        motor.ejecutar(config)
        
        assert len(eventos) == 12  # inicio + 10 aterrizajes + fin
        assert eventos[0] == "inicio"
        assert eventos[-1] == "fin"
    
    def test_diferentes_distribuciones_de_angulo_no_crash(self):
        configs = [
            ConfigExplosion(n_proyectiles=10, semilla=42, dist_angulo="uniforme"),
            ConfigExplosion(n_proyectiles=10, semilla=42, dist_angulo="normal"),
            ConfigExplosion(n_proyectiles=10, semilla=42, dist_angulo="vonmises"),
        ]
        
        for config in configs:
            motor = Explosion(FabricaLigero(), Euler())
            tray, res = motor.ejecutar(config)
            assert len(res) == 10
    
    def test_diferentes_distribuciones_de_velocidad_no_crash(self):
        configs = [
            ConfigExplosion(n_proyectiles=10, semilla=42, dist_velocidad="uniforme"),
            ConfigExplosion(n_proyectiles=10, semilla=42, dist_velocidad="normal"),
            ConfigExplosion(n_proyectiles=10, semilla=42, dist_velocidad="exponencial"),
        ]
        
        for config in configs:
            motor = Explosion(FabricaLigero(), Euler())
            tray, res = motor.ejecutar(config)
            assert len(res) == 10


# Tests de Integraciones.

class TestIntegracion:
    def test_euler_vs_verlet_con_arrastre(self):
        """Con arrastre, Verlet debe dar resultados diferentes a Euler"""
        config = ConfigExplosion(
            n_proyectiles=20, 
            v_min=15, v_max=25, 
            semilla=42,
            dt=0.02
        )
        
        fabrica = FabricaConArrastre()
        
        # Euler
        _, res_euler = Explosion(fabrica, Euler()).ejecutar(config)
        alcances_euler = [r.alcance for r in res_euler]
        
        # Verlet
        _, res_verlet = Explosion(fabrica, Verlet()).ejecutar(config)
        alcances_verlet = [r.alcance for r in res_verlet]
        
        # Deberían ser diferentes (Verlet más preciso)
        assert alcances_euler != alcances_verlet
    
    def test_todas_fabricas_funcionan(self, config_minima):
        fabricas = [
            FabricaLigero(),
            FabricaPesado(),
            FabricaConArrastre()
        ]
        
        for fabrica in fabricas:
            motor = Explosion(fabrica, Euler())
            tray, res = motor.ejecutar(config_minima)
            assert len(res) == config_minima.n_proyectiles
            assert all(r.masa == fabrica._masa for r in res if hasattr(fabrica, '_masa'))