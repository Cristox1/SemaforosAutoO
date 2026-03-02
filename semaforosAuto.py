import pygame
import math
import random
import sys

# Constantes de Entorno
ANCHO, ALTO = 1000, 1000
ANCHO_CARRIL = 40
# Posiciones de las 2 calles verticales y 2 calles horizontales
CALLES_X = [ANCHO // 3, 2 * ANCHO // 3]
CALLES_Y = [ALTO // 3, 2 * ALTO // 3]

# Colores de Semáforo
VERDE = (0, 255, 0)
AMARILLO = (255, 255, 0)
ROJO = (255, 0, 0)

class Semaforo:
    def __init__(self, eje):
        self.eje = eje
        self.estado = ROJO
        
    def establecer_estado(self, nuevo_estado):
        self.estado = nuevo_estado
        
    def obtener_color(self):
        return self.estado

class ControladorInterseccion:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.fase = random.randint(0, 3) # Empezar en fases diferentes
        self.tiempo_amarillo = 60
        self.temporizador = random.randint(0, 60)
        
        # Parámetros auto-organizantes (Requerimientos)
        self.d = 150          # (d) distancia de aproximación
        self.n_umbral = 200   # (n) umbral del contador para cambio
        self.u_min_verde = 120 # (u) tiempo mínimo en verde 
        self.m_pocos = 2       # (m) pocos vehículos cruzando
        self.r_corta = 60      # (r) distancia corta para cruzar verde
        self.e_pasada = 80     # (e) distancia corta e pasando la intersección
        
        self.contador_rojo = 0 # Contador de vehículos acercándose a luz roja
        
        self.luces = {
            'NS': Semaforo('NS'),
            'EO': Semaforo('EO')
        }
        self._aplicar_fase()
        
    def _aplicar_fase(self):
        if self.fase == 0:
            self.luces['NS'].establecer_estado(VERDE)
            self.luces['EO'].establecer_estado(ROJO)
        elif self.fase == 1:
            self.luces['NS'].establecer_estado(AMARILLO)
            self.luces['EO'].establecer_estado(ROJO)
        elif self.fase == 2:
            self.luces['NS'].establecer_estado(ROJO)
            self.luces['EO'].establecer_estado(VERDE)
        elif self.fase == 3:
            self.luces['NS'].establecer_estado(ROJO)
            self.luces['EO'].establecer_estado(AMARILLO)
        elif self.fase == 4:
            self.luces['NS'].establecer_estado(ROJO)
            self.luces['EO'].establecer_estado(ROJO)

    def actualizar(self, autos):
        self.temporizador += 1
        
        autos_ns_acercandose_d = 0
        autos_eo_acercandose_d = 0
        autos_ns_acercandose_r = 0
        autos_eo_acercandose_r = 0
        autos_ns_detenidos_pasando_e = 0
        autos_eo_detenidos_pasando_e = 0

        for a in autos:
            # Vehículos Norte-Sur
            if a.direccion in ['N', 'S'] and abs(a.x - self.x) < 50:
                dist_al_centro = self.y - a.y if a.direccion == 'S' else a.y - self.y
                pasado_centro = a.y - self.y if a.direccion == 'S' else self.y - a.y
                
                if 0 < dist_al_centro < self.d:
                    autos_ns_acercandose_d += 1
                if 0 < dist_al_centro < self.r_corta:
                    autos_ns_acercandose_r += 1
                    
                if 20 < pasado_centro < self.e_pasada and a.velocidad < 0.5:
                    autos_ns_detenidos_pasando_e += 1

            # Vehículos Este-Oeste
            elif a.direccion in ['E', 'O'] and abs(a.y - self.y) < 50:
                dist_al_centro = self.x - a.x if a.direccion == 'E' else a.x - self.x
                pasado_centro = a.x - self.x if a.direccion == 'E' else self.x - a.x
                    
                if 0 < dist_al_centro < self.d:
                    autos_eo_acercandose_d += 1
                if 0 < dist_al_centro < self.r_corta:
                    autos_eo_acercandose_r += 1
                    
                if 20 < pasado_centro < self.e_pasada and a.velocidad < 0.5:
                    autos_eo_detenidos_pasando_e += 1

        # REGLA 6: Si hay vehículos detenidos en ambas direcciones a una distancia corta e pasando la intersección. 
        # cambio a ambas en rojo. Cuando una dirección se libere, cambio de luces a verde en esa dirección.
        if autos_ns_detenidos_pasando_e > 0 and autos_eo_detenidos_pasando_e > 0:
            if self.fase != 4:
                self.fase = 4 # AMBOS EN ROJO
                self._aplicar_fase()
            return # Detiene la evaluación de otras reglas
            
        if self.fase == 4:
            # Recuperación del bloqueo (Fin de Regla 6)
            if autos_ns_detenidos_pasando_e == 0:
                self.fase = 0 # NS Verde
                self.temporizador = 0
                self.contador_rojo = 0
                self._aplicar_fase()
            elif autos_eo_detenidos_pasando_e == 0:
                self.fase = 2 # EO Verde
                self.temporizador = 0
                self.contador_rojo = 0
                self._aplicar_fase()
            return

        cambio_solicitado = False
        
        if self.fase == 0: # NS Verde, EO Rojo
            # REGLA 1: Agregar a un contador el número de vehículos que se acercan a un semáforo en rojo a una distancia d.
            self.contador_rojo += autos_eo_acercandose_d
            
            # REGLA 2: Los semáforos deben de permanecer en verde por un tiempo mínimo u.
            if self.temporizador >= self.u_min_verde:
                # Regla 1 contin... Cuando el contador excede un umbral n, cambio de luces.
                if self.contador_rojo >= self.n_umbral:
                    cambio_solicitado = True
                    
                # REGLA 4: Si no hay vehículo que se acerque a una luz verde a una distancia d y por lo menos un 
                # vehículo se acerca a la luz roja a una distancia d. cambio de luces.
                if autos_ns_acercandose_d == 0 and autos_eo_acercandose_d > 0:
                    cambio_solicitado = True
                    
                # REGLA 3: Si pocos vehículos (m o menos, pero más de cero) estan por cruzar una luz verde 
                # a una distancia corta r. no hacer cambio de luces. (Inhibición del cambio)
                if cambio_solicitado:
                    if 0 < autos_ns_acercandose_r <= self.m_pocos:
                        cambio_solicitado = False
                        
                # REGLA 5: Si hay un vehículo detenido a una distancia corta e pasando una luz verde, cambio de luces.
                # (Sobrescribe la inhibición por pocos vehículos)
                if autos_ns_detenidos_pasando_e > 0:
                    cambio_solicitado = True
                    
            if cambio_solicitado:
                self.fase = 1 # NS Amarillo
                self.temporizador = 0
                self._aplicar_fase()

        elif self.fase == 1: # NS Amarillo -> cambia a EO Verde
            if self.temporizador > self.tiempo_amarillo:
                self.fase = 2
                self.temporizador = 0
                self.contador_rojo = 0 # Regla 1: Reiniciar contador con cambio de luces
                self._aplicar_fase()

        elif self.fase == 2: # EO Verde, NS Rojo
            # Regla 1: Autos acercándose a NS (Rojo)
            self.contador_rojo += autos_ns_acercandose_d
            
            # Regla 2: Tiempo mínimo
            if self.temporizador >= self.u_min_verde:
                # Regla 1
                if self.contador_rojo >= self.n_umbral:
                    cambio_solicitado = True
                    
                # Regla 4
                if autos_eo_acercandose_d == 0 and autos_ns_acercandose_d > 0:
                    cambio_solicitado = True
                    
                # Regla 3 (Inhibición)
                if cambio_solicitado:
                    if 0 < autos_eo_acercandose_r <= self.m_pocos:
                        cambio_solicitado = False
                        
                # Regla 5
                if autos_eo_detenidos_pasando_e > 0:
                    cambio_solicitado = True
                    
            if cambio_solicitado:
                self.fase = 3 # EO Amarillo
                self.temporizador = 0
                self._aplicar_fase()

        elif self.fase == 3: # EO Amarillo -> cambia a NS Verde
            if self.temporizador > self.tiempo_amarillo:
                self.fase = 0
                self.temporizador = 0
                self.contador_rojo = 0 # Regla 1: Reiniciar contador
                self._aplicar_fase()

class Auto:
    def __init__(self, direccion, pos_calle):
        self.direccion = direccion
        self.velocidad = random.uniform(2.5, 4.0)
        self.velocidad_maxima = self.velocidad
        
        self.largo = 26
        self.ancho = 16
        
        desplazamiento_carril = ANCHO_CARRIL // 2
        
        if direccion == 'E': 
            self.x = -self.largo
            self.y = pos_calle + desplazamiento_carril
        elif direccion == 'O':
            self.x = ANCHO + self.largo
            self.y = pos_calle - desplazamiento_carril
        elif direccion == 'S': 
            self.x = pos_calle - desplazamiento_carril
            self.y = -self.largo
        elif direccion == 'N': 
            self.x = pos_calle + desplazamiento_carril
            self.y = ALTO + self.largo

    def actualizar(self, autos, intersecciones):
        dist_a_semaforo = float('inf')
        color_semaforo_relevante = VERDE
        
        # Buscar la intersección más cercana EN FRENTE del coche
        for controlador in intersecciones:
            ix, iy = controlador.x, controlador.y
            
            # Solo consideramos intersecciones en nuestra misma calle
            if self.direccion in ['E', 'O'] and abs(self.y - iy) > ANCHO_CARRIL * 2: continue
            if self.direccion in ['N', 'S'] and abs(self.x - ix) > ANCHO_CARRIL * 2: continue
            
            # Calcular distancia hasta la línea de parada de esta intersección
            dist = float('inf')
            if self.direccion == 'E' and self.x < ix - ANCHO_CARRIL:
                dist = (ix - ANCHO_CARRIL) - (self.x + self.largo / 2)
            elif self.direccion == 'O' and self.x > ix + ANCHO_CARRIL:
                dist = (self.x - self.largo / 2) - (ix + ANCHO_CARRIL)
            elif self.direccion == 'S' and self.y < iy - ANCHO_CARRIL:
                dist = (iy - ANCHO_CARRIL) - (self.y + self.largo / 2)
            elif self.direccion == 'N' and self.y > iy + ANCHO_CARRIL:
                dist = (self.y - self.largo / 2) - (iy + ANCHO_CARRIL)
                
            # Si esta intersección está en frente y es la más cercana vista hasta ahora
            if 0 < dist < dist_a_semaforo:
                dist_a_semaforo = dist
                if self.direccion in ['E', 'O']:
                    color_semaforo_relevante = controlador.luces['EO'].obtener_color()
                else:
                    color_semaforo_relevante = controlador.luces['NS'].obtener_color()

        # Distancia al coche de enfrente
        dist_a_auto = float('inf')
        for otro in autos:
            if otro != self and otro.direccion == self.direccion:
                # Comprobar que están en el mismo carril
                if self.direccion in ['E', 'O'] and abs(otro.y - self.y) > 10: continue
                if self.direccion in ['N', 'S'] and abs(otro.x - self.x) > 10: continue

                dist = float('inf')
                if self.direccion == 'E' and otro.x > self.x:
                    dist = (otro.x - otro.largo/2) - (self.x + self.largo/2)
                elif self.direccion == 'O' and otro.x < self.x:
                    dist = (self.x - self.largo/2) - (otro.x + otro.largo/2)
                elif self.direccion == 'S' and otro.y > self.y:
                    dist = (otro.y - otro.largo/2) - (self.y + self.largo/2)
                elif self.direccion == 'N' and otro.y < self.y:
                    dist = (self.y - self.largo/2) - (otro.y + otro.largo/2)
                    
                if 0 < dist < dist_a_auto: 
                    dist_a_auto = dist

        # Autómata (parar por luz roja/amarilla o por coche al frente)
        velocidad_objetivo = self.velocidad_maxima
        
        # Frena si se acerca a la línea de parada con luz que no sea verde
        if color_semaforo_relevante in [ROJO, AMARILLO] and 0 < dist_a_semaforo < 60:
            velocidad_objetivo = 0  
            
        if dist_a_auto < 30: # Distancia segura al coche de adelante
            velocidad_objetivo = 0 
            
        # Comportamiento de aceleración/frenado
        if self.velocidad < velocidad_objetivo:
            self.velocidad += 0.08
        elif self.velocidad > velocidad_objetivo:
            self.velocidad -= 0.2
            
        self.velocidad = max(0.0, min(self.velocidad, self.velocidad_maxima))

        # Mover coche
        if self.direccion == 'E': self.x += self.velocidad
        elif self.direccion == 'O': self.x -= self.velocidad
        elif self.direccion == 'S': self.y += self.velocidad
        elif self.direccion == 'N': self.y -= self.velocidad

    def dibujar(self, pantalla):
        color = (50, 200, 230) if self.direccion in ['E', 'O'] else (230, 200, 50)
        an = self.largo if self.direccion in ['E', 'O'] else self.ancho
        al = self.ancho if self.direccion in ['E', 'O'] else self.largo
        rect = pygame.Rect(self.x - an/2, self.y - al/2, an, al)
        pygame.draw.rect(pantalla, color, rect, border_radius=3)


def dibujar_fondo(pantalla, intersecciones):
    pantalla.fill((40, 110, 50)) # Pasto
    
    # Calles Horizontales
    for y in CALLES_Y:
        pygame.draw.rect(pantalla, (80, 80, 80), (0, y - ANCHO_CARRIL*1.2, ANCHO, ANCHO_CARRIL*2.4))
    
    # Calles Verticales
    for x in CALLES_X:
        pygame.draw.rect(pantalla, (80, 80, 80), (x - ANCHO_CARRIL*1.2, 0, ANCHO_CARRIL*2.4, ALTO))

    # Semáforos Visuales para cada intersección
    for controlador in intersecciones:
        ix = controlador.x
        iy = controlador.y
        # Detalle central
        pygame.draw.rect(pantalla, (70, 70, 70), (ix - ANCHO_CARRIL*1.2, iy - ANCHO_CARRIL*1.2, ANCHO_CARRIL*2.4, ANCHO_CARRIL*2.4))

        color_ns = controlador.luces['NS'].obtener_color()
        color_eo = controlador.luces['EO'].obtener_color()

        # Dibujar bombitas rojas/verdes en las esquinas de cada intersección
        desplazamientos_ns = [(-1.4, -1.4), (1.4, 1.4)]
        for desp_x, desp_y in desplazamientos_ns:
            pygame.draw.circle(pantalla, (20,20,20), (ix + ANCHO_CARRIL*desp_x, iy + ANCHO_CARRIL*desp_y), 10)
            pygame.draw.circle(pantalla, color_ns, (ix + ANCHO_CARRIL*desp_x, iy + ANCHO_CARRIL*desp_y), 7)

        desplazamientos_eo = [(1.4, -1.4), (-1.4, 1.4)]
        for desp_x, desp_y in desplazamientos_eo:
            pygame.draw.circle(pantalla, (20,20,20), (ix + ANCHO_CARRIL*desp_x, iy + ANCHO_CARRIL*desp_y), 10)
            pygame.draw.circle(pantalla, color_eo, (ix + ANCHO_CARRIL*desp_x, iy + ANCHO_CARRIL*desp_y), 7)


def dibujar_boton_pausa(pantalla, fuente, pausado):
    # Fondo del botón
    color_boton = (180, 50, 50) if pausado else (50, 150, 50)
    rect_boton = pygame.Rect(ANCHO - 160, 10, 150, 40)
    pygame.draw.rect(pantalla, color_boton, rect_boton, border_radius=8)
    pygame.draw.rect(pantalla, (255, 255, 255), rect_boton, 2, border_radius=8)
    
    # Texto del botón
    texto = "▶ REANUDAR" if pausado else "⏸ PAUSAR"
    superficie_texto = fuente.render(texto, True, (255, 255, 255))
    # Centrar texto en el botón
    texto_x = rect_boton.x + (rect_boton.width - superficie_texto.get_width()) // 2
    texto_y = rect_boton.y + (rect_boton.height - superficie_texto.get_height()) // 2
    pantalla.blit(superficie_texto, (texto_x, texto_y))
    
    return rect_boton


def dibujar_overlay_pausa(pantalla, fuente_grande):
    # Overlay semitransparente
    overlay = pygame.Surface((ANCHO, ALTO), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 100))
    pantalla.blit(overlay, (0, 0))
    
    # Texto central de PAUSA
    texto_pausa = fuente_grande.render("⏸ SIMULACIÓN EN PAUSA", True, (255, 255, 255))
    texto_instruccion = pygame.font.SysFont("consolas", 18).render(
        "Presiona ESPACIO o haz clic en el botón para reanudar", True, (200, 200, 200)
    )
    
    pantalla.blit(texto_pausa, (ANCHO // 2 - texto_pausa.get_width() // 2, ALTO // 2 - 30))
    pantalla.blit(texto_instruccion, (ANCHO // 2 - texto_instruccion.get_width() // 2, ALTO // 2 + 20))


def principal():
    pygame.init()
    pantalla = pygame.display.set_mode((ANCHO, ALTO))
    pygame.display.set_caption("Grilla de 4 Intersecciones Auto-organizantes")
    reloj = pygame.time.Clock()
    fuente = pygame.font.SysFont("consolas", 20)
    fuente_grande = pygame.font.SysFont("consolas", 36)

    # Crear 4 controladores de intersección
    intersecciones = []
    for x in CALLES_X:
        for y in CALLES_Y:
            intersecciones.append(ControladorInterseccion(x, y))

    autos = []
    pausado = False
    
    # Control de aparición por carril (8 carriles totales)
    enfriamiento_aparicion = {
        ('N', CALLES_X[0]): 0, ('N', CALLES_X[1]): 0,
        ('S', CALLES_X[0]): 0, ('S', CALLES_X[1]): 0,
        ('E', CALLES_Y[0]): 0, ('E', CALLES_Y[1]): 0,
        ('O', CALLES_Y[0]): 0, ('O', CALLES_Y[1]): 0,
    }

    ejecutando = True
    while ejecutando:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                ejecutando = False
            
            # Pausa con ESPACIO
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_SPACE:
                    pausado = not pausado
            
            # Pausa con clic en el botón
            if evento.type == pygame.MOUSEBUTTONDOWN:
                if evento.button == 1: # Clic izquierdo
                    pos_mouse = pygame.mouse.get_pos()
                    rect_boton = pygame.Rect(ANCHO - 160, 10, 150, 40)
                    if rect_boton.collidepoint(pos_mouse):
                        pausado = not pausado

        # Solo actualizar la simulación si NO está pausada
        if not pausado:
            # Lógica de aparición de múltiples vías
            for clave in enfriamiento_aparicion:
                if enfriamiento_aparicion[clave] > 0:
                    enfriamiento_aparicion[clave] -= 1
                else:
                    if random.random() < 0.015:
                        dir_clave, pos_calle = clave
                        puede_aparecer = True
                        for a in autos:
                            if a.direccion == dir_clave:
                                if dir_clave in ['S', 'N'] and abs(a.x - pos_calle) < 10:
                                    if dir_clave == 'S' and a.y < 120: puede_aparecer = False
                                    if dir_clave == 'N' and a.y > ALTO - 120: puede_aparecer = False
                                elif dir_clave in ['E', 'O'] and abs(a.y - pos_calle) < 10:
                                    if dir_clave == 'E' and a.x < 120: puede_aparecer = False
                                    if dir_clave == 'O' and a.x > ANCHO - 120: puede_aparecer = False
                        
                        if puede_aparecer:
                            autos.append(Auto(dir_clave, pos_calle))
                            enfriamiento_aparicion[clave] = 45
                    
            # Actualizar intersecciones
            for controlador in intersecciones:
                controlador.actualizar(autos)
                
            # Actualizar coches
            for auto in autos:
                auto.actualizar(autos, intersecciones)
                
            # Eliminar coches fuera
            autos = [a for a in autos if -200 < a.x < ANCHO + 200 and -200 < a.y < ALTO + 200]

        # Renderizado (siempre se dibuja, esté pausado o no)
        dibujar_fondo(pantalla, intersecciones)
        for auto in autos:
            auto.dibujar(pantalla)

        # Título en pantalla
        total_vehiculos = fuente.render(f"Vehículos Totales: {len(autos)}", True, (255, 255, 255))
        pantalla.blit(total_vehiculos, (15, 15))
        
        # Botón de pausa
        dibujar_boton_pausa(pantalla, fuente, pausado)
        
        # Overlay de pausa
        if pausado:
            dibujar_overlay_pausa(pantalla, fuente_grande)

        pygame.display.flip()
        reloj.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    principal()