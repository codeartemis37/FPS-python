import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import random
import math

pygame.init()

# Obtenir la résolution de l'écran
infoObject = pygame.display.Info()
display = (infoObject.current_w, infoObject.current_h)
pygame.display.set_mode(display, DOUBLEBUF | OPENGL | pygame.FULLSCREEN)
pygame.mouse.set_visible(False)
pygame.event.set_grab(True)

# Configuration OpenGL
glEnable(GL_DEPTH_TEST)
glMatrixMode(GL_PROJECTION)
gluPerspective(45, (display[0]/display[1]), 0.1, 500.0)
glMatrixMode(GL_MODELVIEW)
glEnable(GL_NORMALIZE)
glShadeModel(GL_SMOOTH)

class Player:
    def __init__(self):
        self.pos = [0, 1, 0]
        self.rot = [0, 0]
        self.speed = 0.1
        self.health = 100
        self.score = 0

class Bot:
    def __init__(self):
        self.pos = [
            random.randint(-20, 20),
            1,
            random.randint(-20, 20)
        ]
        self.speed = 0.05
        self.health = 100

class Bullet:
    def __init__(self, pos, rot):
        self.pos = list(pos)
        self.rot = list(rot)
        self.speed = 0.5
        self.update_vector()

    def update_vector(self):
        self.dx = math.cos(math.radians(self.rot[0])) * math.cos(math.radians(self.rot[1]))
        self.dy = math.sin(math.radians(self.rot[1]))
        self.dz = math.sin(math.radians(self.rot[0])) * math.cos(math.radians(self.rot[1]))

    def update(self):
        self.pos[0] += self.dx * self.speed
        self.pos[1] += self.dy * self.speed
        self.pos[2] += self.dz * self.speed

def draw_cube(pos, size=0.5):
    glPushMatrix()
    glTranslatef(*pos)
    glBegin(GL_QUADS)
    
    # Couleur (rouge pour les bots)
    glColor3f(1, 0, 0)
    
    # Face avant
    glVertex3f(-size, -size, -size)
    glVertex3f(size, -size, -size)
    glVertex3f(size, size, -size)
    glVertex3f(-size, size, -size)
    
    # Face arrière
    glVertex3f(-size, -size, size)
    glVertex3f(size, -size, size)
    glVertex3f(size, size, size)
    glVertex3f(-size, size, size)
    
    # Faces latérales
    glVertex3f(-size, -size, -size)
    glVertex3f(-size, -size, size)
    glVertex3f(-size, size, size)
    glVertex3f(-size, size, -size)
    
    glVertex3f(size, -size, -size)
    glVertex3f(size, -size, size)
    glVertex3f(size, size, size)
    glVertex3f(size, size, -size)
    
    # Haut et bas
    glVertex3f(-size, size, -size)
    glVertex3f(size, size, -size)
    glVertex3f(size, size, size)
    glVertex3f(-size, size, size)
    
    glVertex3f(-size, -size, -size)
    glVertex3f(size, -size, -size)
    glVertex3f(size, -size, size)
    glVertex3f(-size, -size, size)
    
    glEnd()
    glPopMatrix()

player = Player()
bots = [Bot() for _ in range(5)]
bullets = []
mouse_sensitivity = 0.2

clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            pygame.quit()
            quit()
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            bullets.append(Bullet(player.pos, player.rot))

    # Mouvement souris
    mx, my = pygame.mouse.get_rel()
    player.rot[0] += mx * mouse_sensitivity
    player.rot[1] -= -my * mouse_sensitivity
    player.rot[1] = max(-90, min(90, player.rot[1]))

    # Mouvement clavier
    keys = pygame.key.get_pressed()
    forward = [
        math.cos(math.radians(player.rot[0])) * player.speed,
        0,
        math.sin(math.radians(player.rot[0])) * player.speed
    ]
    
    if keys[K_w]:
        player.pos[0] += forward[0]
        player.pos[2] += forward[2]
    if keys[K_s]:
        player.pos[0] -= forward[0]
        player.pos[2] -= forward[2]
    if keys[K_a]:
        player.pos[0] -= forward[2]
        player.pos[2] += forward[0]
    if keys[K_d]:
        player.pos[0] += forward[2]
        player.pos[2] -= forward[0]

    # Mise à jour bots
    for bot in bots:
        dx = player.pos[0] - bot.pos[0]
        dz = player.pos[2] - bot.pos[2]
        distance = math.hypot(dx, dz)
        
        if distance > 1:
            bot.pos[0] += (dx / distance) * bot.speed
            bot.pos[2] += (dz / distance) * bot.speed

    # Mise à jour balles
    for bullet in bullets[:]:
        bullet.update()
        if abs(bullet.pos[0]) > 50 or abs(bullet.pos[2]) > 50:
            bullets.remove(bullet)
            continue
            
        for bot in bots[:]:
            if math.dist(bullet.pos, bot.pos) < 1:
                bots.remove(bot)
                bullets.remove(bullet)
                player.score += 100
                bots.append(Bot())  # Ajouter un nouveau bot
                break

    # Collisions joueur
    for bot in bots:
        if math.dist(player.pos, bot.pos) < 1:
            player.health -= 0.1

    # Rendu 3D
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    
    # Caméra
    glRotatef(-player.rot[1], 1, 0, 0)
    glRotatef(-player.rot[0], 0, 1, 0)
    glTranslatef(-player.pos[0], -player.pos[1], -player.pos[2])

    # Sol
    glBegin(GL_QUADS)
    glColor3f(0.3, 0.3, 0.3)
    for x in range(-20, 20):
        for z in range(-20, 20):
            glVertex3f(x, 0, z)
            glVertex3f(x+1, 0, z)
            glVertex3f(x+1, 0, z+1)
            glVertex3f(x, 0, z+1)
    glEnd()

    # Bots
    for bot in bots:
        draw_cube(bot.pos)

    # Balles
    glColor3f(1, 1, 0)
    for bullet in bullets:
        draw_cube(bullet.pos, 0.2)

    # HUD
    font = pygame.font.SysFont('Arial', 36)
    text_surface = font.render(f"Score: {player.score} | Health: {int(player.health)}", True, (255, 255, 255))
    text_data = pygame.image.tostring(text_surface, "RGBA", True)

    glDisable(GL_DEPTH_TEST)
    glWindowPos2d(10, 10)
    glDrawPixels(text_surface.get_width(), text_surface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, text_data)
    glEnable(GL_DEPTH_TEST)

    pygame.display.flip()
    clock.tick(60)
