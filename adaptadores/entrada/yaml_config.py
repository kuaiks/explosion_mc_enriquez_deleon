import yaml # para leer archivos YAML con la configuración de la simulación,  existe como puente porque el dominio no debería depender de esta librería, pero el adaptador sí.
from pathlib import Path # este sirve para trabajar con rutas y archivos.
from dominio.modelos import ConfigExplosion # para definir la estructura de la configuración que el dominio espera (otra vez)


def cargar_config_yaml(ruta: str = "config.yaml") -> ConfigExplosion: 
    path = Path(ruta) # convertimos la ruta a un objeto Path para manejarla mejor

    # Si el 'config.yaml' no funciona crea una configuración limpia con valores vacíos/por
    # defecto para que el programa no se caiga.

    if not path.exists():
        return ConfigExplosion()

    with open(path, "r", encoding="utf-8") as f: # abrimos el archivo en modo lectura 
        datos = yaml.safe_load(f) or {} # cargamos el YAML y si está vacío usamos un diccionario vacío para evitar errores.
        

    sim  = datos.get("simulacion", {})
    viz  = datos.get("visualizacion", {})
    dist = datos.get("distribucion", {})
    ejec = datos.get("ejecucion", {})
    ang = dist.get("angulo", {})
    vel = dist.get("velocidad", {})
    
    return ConfigExplosion(
        n_proyectiles  = sim.get("n_proyectiles", 300),
        v_min          = sim.get("v_min", 5.0),
        v_max          = sim.get("v_max", 30.0),
        g              = sim.get("g", 9.8),
        dt             = sim.get("dt", 0.04),
        semilla        = sim.get("semilla", 42),
        trail_length   = viz.get("trail", 18),
        dist_angulo    = ang.get("tipo", "uniforme"),
        angulo_media   = ang.get("media", 90.0),
        angulo_sigma   = ang.get("sigma", 20.0),
        angulo_kappa   = ang.get("kappa", 6.0),
        dist_velocidad = vel.get("tipo", "uniforme"),
        vel_media      = vel.get("media", 12.0),
        vel_sigma      = vel.get("sigma", 4.0),
        modo_ejecucion = ejec.get("modo", "secuencial"),
        workers        = ejec.get("workers", None),
    ) # devolvemos una instancia de ConfigExplosion con los valores cargados del YAML o los valores por defecto si no están presentes.
