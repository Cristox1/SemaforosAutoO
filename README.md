# Semáforos Auto-organizantes - Simulación con Pygame

Simulación visual de un cruce de **4 intersecciones** con semáforos que se auto-organizan basándose en las 6 reglas de Carlos Gershenson, implementada en Python con Pygame.

## Descripción

Este proyecto implementa un sistema de **semáforos auto-organizantes** que toman decisiones de cambio de luces de manera autónoma, sin un controlador central. Cada intersección evalúa las condiciones del tráfico a su alrededor y aplica un conjunto de **6 reglas** para determinar cuándo cambiar el estado de sus semáforos.

La simulación modela:
- **2 calles verticales** y **2 calles horizontales**.
- Vehículos que se desplazan en **4 direcciones**.
- Semáforos con estados **Verde**, **Amarillo** y **Rojo**.
- Aparición aleatoria de vehículos en cada carril.
- Comportamiento de frenado y aceleración de los vehículos (autómata celular).

---

## Reglas de Auto-organización para semaforos

Cada intersección aplica las siguientes reglas de manera independiente para decidir el cambio de luces:

### Regla 1 — Contador de vehículos en rojo
> En cada intervalo de tiempo, agregar a un **contador** el número de vehículos que se acercan a un semáforo en **rojo** a una distancia **d**. Cuando el contador excede un umbral **n**, cambio de luces. *(Reiniciar contador con cambio de luces.)*

| Parámetro | Valor | Descripción |
|-----------|-------|-------------|
| `d` | 150 px | Distancia de aproximación |
| `n` | 200 | Umbral del contador para cambio |

### Regla 2 — Tiempo mínimo en verde
> Los semáforos deben de permanecer en **verde** por un tiempo mínimo **u**.

| Parámetro | Valor | Descripción |
|-----------|-------|-------------|
| `u` | 120 ticks | Tiempo mínimo en verde |

### Regla 3 — Inhibición por pocos vehículos
> Si **pocos vehículos** (**m** o menos, pero más de cero) están por cruzar una luz **verde** a una distancia corta **r**, **no hacer cambio** de luces.

| Parámetro | Valor | Descripción |
|-----------|-------|-------------|
| `m` | 2 | Umbral de pocos vehículos |
| `r` | 60 px | Distancia corta para cruzar verde |

### Regla 4 — Sin vehículos en verde, con vehículos en rojo
> Si **no hay** vehículo que se acerque a una luz **verde** a una distancia **d** y **por lo menos un** vehículo se acerca a la luz **roja** a una distancia **d**, cambio de luces.

### Regla 5 — Vehículo detenido pasando luz verde
> Si hay un vehículo **detenido** a una distancia corta **e** pasando una luz **verde**, cambio de luces. *(Sobrescribe la inhibición de la Regla 3.)*

| Parámetro | Valor | Descripción |
|-----------|-------|-------------|
| `e` | 80 px | Distancia corta pasando la intersección |

### Regla 6 — Bloqueo mutuo
> Si hay vehículos **detenidos en ambas direcciones** a una distancia corta **e** pasando la intersección, cambio a **ambas en rojo**. Cuando una dirección se libere, cambio de luces a **verde** en esa dirección.


## Instalación y Ejecución

### Prerrequisitos
- Python 3.12 o superior
- Pygame

