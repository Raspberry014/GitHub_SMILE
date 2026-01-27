import pygame
import sys
import random
import time

# Инициализация
pygame.init()

SCREEN_W, SCREEN_H = 800, 600
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Смена времени суток каждые 5 секунд")

clock = pygame.time.Clock()

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (100, 100, 100)
DARK_GRAY = (60, 60, 60)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
WINDOW_LIGHT = (255, 255, 150)
BLUE_DAY = (135, 206, 250)
ORANGE = (255, 180, 100)
DARK_BLUE = (25, 25, 50)

# Облака
clouds = [{'x': random.randint(0, SCREEN_W), 'y': random.randint(50, 200),
           'size': random.randint(60, 120), 'speed': random.uniform(0.2, 0.7)} for _ in range(7)]

# Здания с окнами
buildings = []
for i in range(9):
    width = 80
    height = random.randint(150, 400)
    x = i * 100
    cols = 4
    rows = height // 40
    windows = []
    for r in range(rows):
        for c in range(cols):
            windows.append({'x': x + 5 + c*18, 'y': SCREEN_H - height + 5 + r*35, 'on': False})
    buildings.append({'x': x, 'width': width, 'height': height, 'windows': windows})

# Самолёты
class Plane:
    def __init__(self, y, speed):
        self.x = -100 - random.randint(0, 300)
        self.y = y
        self.speed = speed
        self.trail = []

    def update(self):
        self.x += self.speed
        self.trail.append((self.x, self.y + 15))
        if len(self.trail) > 20:
            self.trail.pop(0)
        if self.x > SCREEN_W + 100:
            self.x = -100
            self.trail = []

    def draw(self, surface):
        for i, pos in enumerate(self.trail):
            alpha = int(255 * (i / len(self.trail)))
            s = pygame.Surface((6, 6), pygame.SRCALPHA)
            s.fill((200, 200, 200, alpha))
            surface.blit(s, (pos[0], pos[1]))
        pygame.draw.polygon(surface, RED, [(self.x, self.y),(self.x+60,self.y+15),(self.x,self.y+30)])
        pygame.draw.rect(surface, YELLOW, (self.x + 20, self.y + 5, 30, 10))

# Птицы
class Bird:
    def __init__(self):
        self.x = random.randint(0, SCREEN_W)
        self.y = random.randint(100, 300)
        self.speed = random.uniform(1, 2)

    def update(self):
        self.x += self.speed
        if self.x > SCREEN_W:
            self.x = -50
            self.y = random.randint(100, 300)

    def draw(self, surface):
        pygame.draw.line(surface, BLACK, (self.x, self.y), (self.x+10, self.y-5), 2)
        pygame.draw.line(surface, BLACK, (self.x+10, self.y-5), (self.x+20, self.y), 2)

planes = [Plane(150,3), Plane(100,2), Plane(200,4)]
birds = [Bird() for _ in range(5)]

# Таймер анимации
start_time = time.time()
duration = 180  # 3 минуты

# Состояния суток
time_of_day_names = ["Утро", "День", "Вечер", "Ночь"]
time_of_day_colors = [ORANGE, BLUE_DAY, ORANGE, DARK_BLUE]  # фон
time_of_day_windows = [
    2,   # утро: 1-2 окна
    0,   # день: окна выключены
    4,   # вечер: несколько окон
    10   # ночь: почти все окна
]

while True:
    current_time = time.time()
    if current_time - start_time > duration:
        pygame.quit()
        sys.exit()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Определяем текущее время суток (каждые 5 секунд смена)
    seconds_passed = int(current_time - start_time)
    time_index = (seconds_passed // 5) % 4  # 0-3
    sky_color = time_of_day_colors[time_index]
    screen.fill(sky_color)

    # Солнце и Луна
    if time_index in [0,1,2]:  # утро, день, вечер
        pygame.draw.circle(screen, YELLOW, (100, 100), 40)
    else:  # ночь
        pygame.draw.circle(screen, WHITE, (700, 100), 40)

    # Цвет облаков
    if time_index == 3:  # Ночь
        cloud_color = (180, 180, 180)
    else:
        cloud_color = WHITE

    # Облака
    for cloud in clouds:
        pygame.draw.ellipse(screen, cloud_color, (cloud['x'], cloud['y'], cloud['size']*2, cloud['size']))
        cloud['x'] += cloud['speed']
        if cloud['x'] > SCREEN_W + cloud['size']:
            cloud['x'] = -cloud['size']*2
            cloud['y'] = random.randint(50,200)
            cloud['speed'] = random.uniform(0.2,0.7)

    # Здания с окнами
    for b in buildings:
        pygame.draw.rect(screen, DARK_GRAY, (b['x'], SCREEN_H - b['height'], b['width'], b['height']))
        pygame.draw.rect(screen, GRAY, (b['x'] + 5, SCREEN_H - b['height'], b['width'] - 10, b['height']))
        # Включаем нужное количество окон
        num_windows_on = time_of_day_windows[time_index]
        for i, w in enumerate(b['windows']):
            w['on'] = True if i < num_windows_on else False
            color = WINDOW_LIGHT if w['on'] else BLACK
            pygame.draw.rect(screen, color, (w['x'], w['y'], 12, 20))

    # Самолёты
    for plane in planes:
        plane.update()
        plane.draw(screen)

    # Птицы
    for bird in birds:
        bird.update()
        bird.draw(screen)

    pygame.display.flip()
    clock.tick(60)
