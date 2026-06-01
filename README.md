#  Explosión Monte Carlo - Laboratorio de Simulación

**Simulación de explosión con patrones de diseño y arquitectura hexagonal**

Simulación Monte Carlo de una explosión desde un punto central. Se lanzan **N proyectiles simultáneamente** con ángulos y velocidades aleatorias, siguiendo diferentes distribuciones estadísticas. 

**Características principales:**
- **3 patrones de diseño**: Factory Method, Strategy y Observer implementados.
- **Arquitectura hexagonal**: El dominio del proyecto está completamente desacoplado de la interfaz.
- **Múltiples distribuciones**: Uniforme, Normal para los proyectiles. Para los ángulos también se implementa Von Mises y exponencial para las velocidades.
- **Animación en tiempo real**: Visualización con matplotlib en tiempo real.
- **Exportación CSV**:
- **Tests unitarios**: 

---

## Integrantes

| Nombre | GitHub |
|--------|--------|
| Esdras de León | [@essdras](https://github.com/essdras) |
| Daniel Enriquez 202308323| [@kuaiks](https://github.com/kuaiks) |

---

## Instalación

### Dependencias

- Python 3.10 o superior


### Instalación 

```bash
# Clonar el repositorio
git clone https://github.com/kuaiks/explosion_mc_enriquez_deleon
cd explosion_mc_enriquez_deleon

# Ver los comandos del programa
make help

# Instalar dependencias y crear entorno virtual
make install
