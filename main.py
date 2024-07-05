import pgzrun
import math

# Tamaño de la ventana
WIDTH = 1024
HEIGHT = 768

# Estado inicial del juego
estado_juego = "menu"
nivel_actual = 1
disparos_restantes = 1  # Inicializar con 1 disparo para todos los niveles
brazo_golpeado = False  # Indica si el brazo ha sido golpeado
target_caida_vy = 0  # Velocidad de caída del objetivo
disparo = False  # Indica si se ha disparado la flecha

niveles = [
    {"objetivo_pos": (900, 280), "personaje_pos": (80, 330), "flecha_pos": (120, 310), "gravedad": 9.8,
     "fondo": "background1", "cajas": []},
    {"objetivo_pos": (900, 680), "personaje_pos": (100, 670), "flecha_pos": (140, 650), "gravedad": 8.5,
     "fondo": "background2", "cajas": [(500, 700)]},  # Solo una caja de paja
    {"objetivo_pos": (700, 500), "personaje_pos": (120, 290), "flecha_pos": (160, 270), "gravedad": 10.0,
     "fondo": "background3", "cajas": []},
]

angulo_flecha = 45
potencia_flecha = 10
flecha = Actor('arrow', niveles[nivel_actual - 1]["flecha_pos"])
personaje = Actor('character', niveles[nivel_actual - 1]["personaje_pos"])  # Imagen del personaje ajustada
objetivo = Actor('target1', niveles[nivel_actual - 1]["objetivo_pos"])
fondo = Actor(niveles[nivel_actual - 1]["fondo"], (WIDTH // 2, HEIGHT // 2))
cajas = [Actor('caja_paja', pos) for pos in niveles[nivel_actual - 1]["cajas"]]
flecha_vx = 0
flecha_vy = 0

# Para el último nivel
brazo = Actor('image', (niveles[-1]["objetivo_pos"][0], 200))  # Brazo en el último nivel
brazo_velocidad = 2
target_velocidad = 2

# Botones del menú
boton_empezar = Rect((WIDTH // 2 - 150, HEIGHT // 2 - 50), (300, 60))
boton_creditos = Rect((WIDTH // 2 - 150, HEIGHT // 2 + 30), (300, 60))


def draw():
    screen.clear()
    fondo.draw()

    if estado_juego == "menu":
        screen.draw.text("Robin Hood", center=(WIDTH // 2, HEIGHT // 2 - 150), owidth=0.5, ocolor=(0, 0, 0),
                         color="white", fontsize=70)
        screen.draw.filled_rect(boton_empezar, (0, 128, 0))
        screen.draw.text("Empezar Juego", center=(WIDTH // 2, HEIGHT // 2 - 20), owidth=0.5, ocolor=(0, 0, 0),
                         color="white", fontsize=50)
        screen.draw.filled_rect(boton_creditos, (0, 0, 128))
        screen.draw.text("Créditos", center=(WIDTH // 2, HEIGHT // 2 + 60), owidth=0.5, ocolor=(0, 0, 0), color="white",
                         fontsize=50)
    elif estado_juego == "creditos":
        screen.draw.text("Autores:", center=(WIDTH // 2, HEIGHT // 2 - 100), owidth=0.5, ocolor=(0, 0, 0),
                         color="white", fontsize=50)
        screen.draw.text("Juan Camilo Parado", center=(WIDTH // 2, HEIGHT // 2 - 50), owidth=0.5, ocolor=(0, 0, 0),
                         color="white", fontsize=40)
        screen.draw.text("Alanis Nicole Forero", center=(WIDTH // 2, HEIGHT // 2), owidth=0.5, ocolor=(0, 0, 0),
                         color="white", fontsize=40)
        screen.draw.text("Presiona SPACE para volver", center=(WIDTH // 2, HEIGHT // 2 + 100), owidth=0.5,
                         ocolor=(0, 0, 0), color="white", fontsize=40)
    else:
        objetivo.draw()
        flecha.draw()
        personaje.draw()
        for caja in cajas:
            caja.draw()

        if nivel_actual == len(niveles):
            brazo.draw()
            for j in range(-2, 3):  # Dibujar varias líneas para simular un grosor mayor horizontalmente
                screen.draw.line((0, brazo.y - 120 + j), (WIDTH, brazo.y - 120 + j), (255, 255, 255))
            if not brazo_golpeado:
                objetivo.pos = (brazo.x, brazo.y + 150)  # Ajustar la posición del objetivo

        if estado_juego == "apuntando":
            dibujar_trayectoria(flecha.x, flecha.y, angulo_flecha, potencia_flecha, 30, 255, 0, 0)

        screen.draw.text(f"Ángulo: {angulo_flecha}", (10, 10), color="black")
        screen.draw.text(f"Potencia: {potencia_flecha}", (10, 30), color="black")

        if estado_juego == "acierto":
            screen.draw.text("¡Acertaste!", center=(WIDTH // 2, HEIGHT // 2), owidth=0.5, ocolor=(0, 0, 0), color="red",
                             fontsize=50)
        elif estado_juego == "fallo":
            screen.draw.text("¡Fallaste!", center=(WIDTH // 2, HEIGHT // 2), owidth=0.5, ocolor=(0, 0, 0), color="red",
                             fontsize=50)


def dibujar_trayectoria(x, y, angulo, potencia, pasos, r, g, b):
    vx = potencia * math.cos(math.radians(angulo))
    vy = -potencia * math.sin(math.radians(angulo))
    for paso in range(pasos):
        t = paso * 0.1
        dx = vx * t
        dy = vy * t + 0.5 * niveles[nivel_actual - 1]["gravedad"] * (t ** 2)
        nx = x + dx
        ny = y + dy
        if paso % 2 == 0:  # Crear un efecto discontinuo
            screen.draw.line((x, y), (nx, ny), (r, g, b))
        x, y = nx, ny


def update():
    global estado_juego, flecha_vx, flecha_vy, nivel_actual, disparos_restantes, brazo_velocidad, brazo_golpeado, target_caida_vy
    if estado_juego == "volando":
        flecha.x += flecha_vx
        flecha.y += flecha_vy
        flecha_vy += niveles[nivel_actual - 1]["gravedad"] * 0.1  # Ajuste para la gravedad por frame (asumiendo 60 fps)

        if flecha.colliderect(objetivo):
            if nivel_actual < len(niveles):
                estado_juego = "acierto"
            else:
                estado_juego = "acierto"
        elif flecha.y > HEIGHT or flecha.x > WIDTH or flecha.x < 0 or any(flecha.colliderect(caja) for caja in cajas):
            if nivel_actual == 2 and disparos_restantes > 0:
                disparos_restantes -= 1
                if any(flecha.colliderect(caja) for caja in cajas):
                    cajas.clear()  # Eliminar las cajas si son golpeadas
                reiniciar_flecha()
            else:
                estado_juego = "fallo"

    if nivel_actual == len(niveles):
        if brazo_golpeado:
            target_caida_vy += niveles[nivel_actual - 1]["gravedad"] * 0.1
            objetivo.y += target_caida_vy
            if objetivo.y > HEIGHT:
                estado_juego = "fallo"
        else:
            brazo.x += brazo_velocidad
            if brazo.x >= WIDTH - 50 or brazo.x <= 50:
                brazo_velocidad *= -1

    if flecha.colliderect(brazo) and disparo:
        brazo_golpeado = True


def reiniciar_flecha():
    global angulo_flecha, potencia_flecha, flecha_vx, flecha_vy, estado_juego, disparo
    angulo_flecha = 45
    potencia_flecha = 10
    flecha.pos = niveles[nivel_actual - 1]["flecha_pos"]
    flecha_vx = 0
    flecha_vy = 0
    disparo = False
    estado_juego = "apuntando"


def on_key_down(key):
    global angulo_flecha, potencia_flecha, estado_juego, flecha_vx, flecha_vy, nivel_actual, disparos_restantes, disparo
    if estado_juego == "menu":
        if key == keys.SPACE:
            estado_juego = "apuntando"
        elif key == keys.SPACE and estado_juego == "creditos":
            estado_juego = "menu"
    elif estado_juego == "apuntando":
        if key == keys.UP:
            angulo_flecha = min(angulo_flecha + 1, 90)
        elif key == keys.DOWN:
            angulo_flecha = max(angulo_flecha - 1, 0)
        elif key == keys.RIGHT:
            potencia_flecha = min(potencia_flecha + 1, 100)
        elif key == keys.LEFT:
            potencia_flecha = max(potencia_flecha - 1, 0)
        elif key == keys.SPACE:
            flecha_vx = potencia_flecha * math.cos(math.radians(angulo_flecha)) * 0.5  # Ajuste de escala
            flecha_vy = -potencia_flecha * math.sin(math.radians(angulo_flecha)) * 0.5  # Ajuste de escala
            estado_juego = "volando"
            disparo = True
    elif estado_juego == "acierto" and key == keys.SPACE:
        if nivel_actual < len(niveles):
            nivel_actual += 1
            disparos_restantes = 2 if nivel_actual == 2 else 1  # Dos disparos en el segundo nivel
            reiniciar_nivel()
        else:
            estado_juego = "menu"


def on_mouse_down(pos):
    global estado_juego
    if estado_juego == "menu":
        if boton_empezar.collidepoint(pos):
            estado_juego = "apuntando"
        elif boton_creditos.collidepoint(pos):
            estado_juego = "creditos"


def reiniciar_nivel():
    global angulo_flecha, potencia_flecha, flecha, objetivo, fondo, cajas, flecha_vx, flecha_vy, estado_juego, personaje, brazo_golpeado, disparo
    angulo_flecha = 45
    potencia_flecha = 10
    flecha.pos = niveles[nivel_actual - 1]["flecha_pos"]
    objetivo.pos = niveles[nivel_actual - 1]["objetivo_pos"]
    fondo.image = niveles[nivel_actual - 1]["fondo"]
    personaje.pos = niveles[nivel_actual - 1]["personaje_pos"]
    cajas = [Actor('caja_paja', pos) for pos in niveles[nivel_actual - 1]["cajas"]]
    flecha_vx = 0
    flecha_vy = 0
    brazo_golpeado = False  # Resetear el estado del brazo
    disparo = False
    estado_juego = "apuntando"


pgzrun.go()
