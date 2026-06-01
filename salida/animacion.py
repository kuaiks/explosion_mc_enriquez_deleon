import math
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
from matplotlib.collections import LineCollection # para dibujar las estelas de los proyectiles de forma eficiente,dibujar MUCHAS líneas juntas como una sola colección optimizada.
import matplotlib
matplotlib.use('TkAgg')  # Esto configura el backend gráfico.
import matplotlib.pyplot as plt  
import matplotlib.animation as animation

from dominio.modelos import ConfigExplosion, ResultadoProyectil # para definir la configuración de la simulación y la estructura de los resultados que el dominio espera.
from dominio.puertos import PuertoSalida # para cumplir con la interfaz de salida que el dominio espera, esta clase se encargará de mostrar la animación de la simulación usando Matplotlib.


# ------ Colores -------------------------------------------------------
BG = "#0a0f0a"   
GREEN = "#00ff41"   
GREEN_DK = "#005512"   
ORANGE = "#ff8c00"   
TEXT_COL = "#00cc33"   


class SalidaAnimacion(PuertoSalida):

    def mostrar(
        self,
        config: ConfigExplosion,
        trayectorias: list,
        resultados: list, 
    ) -> None: 
        trail = config.trail_length
        n     = len(trayectorias)

        # ------ Límites del área ------------------------------------------------------
        # Para evitar que los proyectiles se salgan de la pantalla escaneamos todas las trayectorias antes de 
        # dibujar y ajustamos los ejes
        all_x = [pt[0] for tray in trayectorias for pt in tray] # esto es una lista de todas las coordenadas x de todas las trayectorias, lo mismo para y. Esto nos permite encontrar los límites máximos para ajustar la vista.
        all_y = [pt[1] for tray in trayectorias for pt in tray]
        x_abs = max(abs(min(all_x)), abs(max(all_x))) * 1.05 if all_x else 100 
        y_max = max(all_y) * 1.10 if all_y else 50

        alcances = [r.alcance for r in resultados] 
        alc_min  = min(alcances)
        alc_max  = max(alcances)
        bins     = np.linspace(alc_min * 1.1, alc_max * 1.1, 40) # para el histograma de alcances, ajustamos los límites un poco más allá del mínimo y máximo para que se vean mejor las barras.

        # ------ Figura con GridSpec ------------------------------------------------------
        # solo divide la pantalla en una cuadrícula.
        fig = plt.figure(figsize=(14, 7), facecolor=BG)
        fig.patch.set_facecolor(BG)

        gs = fig.add_gridspec(
            2, 2,
            width_ratios=[2.2, 1],
            height_ratios=[1.6, 1],
            hspace=0.35,
            wspace=0.25,
        )

        ax_tray  = fig.add_subplot(gs[:, 0])   
        ax_hist  = fig.add_subplot(gs[0, 1])   
        ax_stats = fig.add_subplot(gs[1, 1])   

        for ax in (ax_tray, ax_hist, ax_stats):
            ax.set_facecolor(BG)
            for spine in ax.spines.values():
                spine.set_color(GREEN_DK)
            ax.tick_params(colors=GREEN, labelsize=7)

        # ------ Panel trayectorias -----------------------------------------------------
        ax_tray.set_xlim(-x_abs, x_abs)
        ax_tray.set_ylim(0, y_max)
        ax_tray.set_xlabel("x (m)", color=GREEN, fontsize=8)
        ax_tray.set_ylabel("y (m)", color=GREEN, fontsize=8)
        ax_tray.axhline(0, color=GREEN_DK, linewidth=0.6)
        ax_tray.axvline(0, color=GREEN_DK, linewidth=0.6, linestyle="--")

        titulo_tray = ax_tray.set_title("", color=GREEN, fontsize=9, pad=6)

        col_estelas = LineCollection([], linewidths=0.8, alpha=0.7, colors=[GREEN])
        ax_tray.add_collection(col_estelas)

        scatter_imp = ax_tray.scatter(
            [], [], marker="x", color=ORANGE, s=18, linewidths=0.8, zorder=5
        )

        # Punto de origen
        ax_tray.scatter([0], [0], color=GREEN, s=40, zorder=6, marker="o")

        # ------ Panel histograma --------------------------------------------------
        ax_hist.set_title("distribución  de  alcances", color=GREEN, fontsize=8, pad=4)
        ax_hist.set_xlabel("alcance (m)", color=GREEN, fontsize=7)
        ax_hist.set_ylabel("frecuencia",  color=GREEN, fontsize=7)

        # ------ Panel estadísticas --------------------------------------------------
        ax_stats.axis("off")
        stats_text = ax_stats.text(
            0.05, 0.95, "iniciando...",
            transform=ax_stats.transAxes,
            color=TEXT_COL, fontsize=8,
            verticalalignment="top",
            fontfamily="monospace",
        )

        max_frames = max(len(t) for t in trayectorias)
        # ------ Funciones Internas de Simulación en Tiempo Real -------------------------------
        def _segmentos_estela(frame):
            segs = []
            for tray in trayectorias:
                if frame >= len(tray):
                    continue
                ini = max(0, frame - trail)
                puntos = tray[ini: frame + 1]
                if frame >= len(tray) -1:
                    puntos = []

                if len(puntos) >= 2:
                    segs.append(puntos)
            return segs

        def _impactos_hasta(frame):
            xs = []
            for tray in trayectorias:
                if frame >= len(tray) - 1:
                    xs.append(tray[-1][0])
            return xs

        # ------ Función de actualización --------------------------------------------------
        def actualizar(frame):

            col_estelas.set_segments(_segmentos_estela(frame))


            ix = _impactos_hasta(frame)
            if ix:
                col_imp = np.column_stack([ix, [0.0] * len(ix)])
            else:
                col_imp = np.empty((0, 2))
            scatter_imp.set_offsets(col_imp)


            aterrizados = sum(1 for t in trayectorias if frame >= len(t) - 1)
            en_vuelo    = n - aterrizados
            t_sim       = frame * config.dt


            label_ang = {
                "uniforme":  "ángulo uniforme",
                "normal":    f"ángulo normal (σ={config.angulo_sigma:.0f}°)",
                "vonmises":  f"ángulo vonMises (κ={config.angulo_kappa:.1f}, μ={config.angulo_media:.0f}°)",
            }.get(config.dist_angulo, config.dist_angulo)

            label_vel = {
                "uniforme":    "vel uniforme",
                "normal":      f"vel normal (μ={config.vel_media:.0f})",
                "exponencial": f"vel exponencial (μ={config.vel_media:.0f} m/s)",
            }.get(config.dist_velocidad, config.dist_velocidad)

            titulo_tray.set_text(
                f"EXPLOSIÓN  —  {label_ang}  ·  {label_vel}\n"
                f"t = {t_sim:.2f} s   |   en vuelo: {en_vuelo}   |   aterrizados: {aterrizados}"
            )


            if frame % 4 == 0 or frame == max_frames - 1:
                alc_hasta = [
                    resultados[i].alcance
                    for i, tray in enumerate(trayectorias)
                    if frame >= len(tray) - 1
                ]
                ax_hist.cla()
                ax_hist.set_facecolor(BG)
                for spine in ax_hist.spines.values():
                    spine.set_color(GREEN_DK)
                ax_hist.tick_params(colors=GREEN, labelsize=7)
                ax_hist.set_title("distribución  de  alcances", color=GREEN, fontsize=8, pad=4)
                ax_hist.set_xlabel("alcance (m)", color=GREEN, fontsize=7)
                ax_hist.set_ylabel("frecuencia",  color=GREEN, fontsize=7)
                if alc_hasta:
                    ax_hist.hist(
                        alc_hasta, bins=bins,
                        color=GREEN, edgecolor=BG, linewidth=0.3, alpha=0.85,
                    )


            if aterrizados > 0:
                alc_hasta = [
                    resultados[i].alcance
                    for i, tray in enumerate(trayectorias)
                    if frame >= len(tray) - 1
                ]
                avg = sum(alc_hasta) / len(alc_hasta)
                std = math.sqrt(sum((x - avg) ** 2 for x in alc_hasta) / len(alc_hasta))
                stats_text.set_text(
                    f"proyectiles : {aterrizados}\n\n"
                    f"máximo      : {max(alc_hasta):>8.1f} m\n"
                    f"mínimo      : {min(alc_hasta):>8.1f} m\n"
                    f"promedio    : {avg:>8.1f} m\n"
                    f"desv. std   : {std:>8.1f} m"
                )

            return col_estelas, scatter_imp, titulo_tray, stats_text

        # ------ Lanzar animación --------------------------------------------------
        ani = animation.FuncAnimation(
            fig,
            actualizar,
            frames=max_frames,
            interval=30,
            blit=False,
            repeat=False,
        )

        plt.tight_layout(pad=1.2)
        plt.show()
