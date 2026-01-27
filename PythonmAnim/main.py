# knight_vs_monsters.py
import pygame
import sys
import random
import os

# -------------- Настройки --------------
SCREEN_W, SCREEN_H = 1500, 750
FPS = 60

# Пути к ресурсам (положи PNG рядом с этим скриптом)
FOREST_FILE = "forest.png"
KNIGHT_FILE = "knight.png"
MONSTER_FILES = ["monster.png", "monster2.png", "monster3.png"]
BONUS_FILE = "bonus.png"

# Игровые параметры (настройки, схожие с твоим C++ кодом)
PLAYER_START_POS = (SCREEN_W // 3, SCREEN_H // 2)
PLAYER_HEALTH = 100
PLAYER_SPEED = 200.0
PLAYER_SCALE = 0.2
PLAYER_ATTACK_COOLDOWN = 1.0
PLAYER_DAMAGE_INTERVAL = 1.5

MONSTER_SPEEDS = [100.0, 120.0, 80.0]
MONSTER_SCALES = [0.2, 0.2, 0.19]
MONSTER_HEALTHS = [50, 60, 70]
MONSTER_RESPAWN_TIME = 3.0

BONUS_SCALE = 0.7
BONUS_RESPAWN_INTERVAL = 10.0

# -------------- Инициализация --------------
pygame.init()
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
pygame.display.set_caption("Knight vs Monsters (Pygame) — Еркасов Т. CS-302(c)")
clock = pygame.time.Clock()
font_small = pygame.font.SysFont("arial", 20)
font_big = pygame.font.SysFont("arial", 36)

# -------------- Загрузка текстур (с защитой) --------------
def load_image_safe(path, convert_alpha=True):
    if not os.path.isfile(path):
        return None
    try:
        img = pygame.image.load(path)
        return img.convert_alpha() if convert_alpha else img.convert()
    except Exception as e:
        print(f"Error loading {path}: {e}")
        return None

# фон (растянуть под экран)
bg_img = load_image_safe(FOREST_FILE, convert_alpha=False)
if bg_img:
    bg_img = pygame.transform.scale(bg_img, (SCREEN_W, SCREEN_H))

player_img = load_image_safe(KNIGHT_FILE)
monster_imgs = [load_image_safe(p) for p in MONSTER_FILES]
bonus_img = load_image_safe(BONUS_FILE)

# Если нет монстров по файлам - используем игрока как заглушку
for i in range(len(monster_imgs)):
    if monster_imgs[i] is None:
        monster_imgs[i] = player_img  # может быть None — обработим дальше

# -------------- Структуры состояния --------------
class Player:
    def __init__(self):
        self.pos = pygame.Vector2(*PLAYER_START_POS)
        self.health = PLAYER_HEALTH
        self.speed = PLAYER_SPEED
        self.scale = PLAYER_SCALE
        self.attack_cooldown = 0.0
        self.damage_timer = 0.0

    @property
    def size(self):
        if player_img:
            return (int(player_img.get_width() * self.scale), int(player_img.get_height() * self.scale))
        return (60, 100)

class Monster:
    def __init__(self, idx, image):
        self.idx = idx
        self.image = image
        self.scale = MONSTER_SCALES[idx]
        self.speed = MONSTER_SPEEDS[idx]
        self.max_health = MONSTER_HEALTHS[idx]
        self.health = self.max_health
        self.respawn_timer = 0.0
        self.pos = pygame.Vector2(random.randrange(0, SCREEN_W), random.randrange(0, SCREEN_H))

    @property
    def size(self):
        if self.image:
            return (int(self.image.get_width() * self.scale), int(self.image.get_height() * self.scale))
        return (120, 140)

class Bonus:
    def __init__(self, image):
        self.image = image
        self.active = False
        self.timer = 0.0
        self.pos = pygame.Vector2(0,0)
        self.scale = BONUS_SCALE

    @property
    def size(self):
        if self.image:
            return (int(self.image.get_width() * self.scale), int(self.image.get_height() * self.scale))
        return (40,40)

# -------------- Создаём сущности --------------
player = Player()
monsters = [Monster(i, monster_imgs[i] if i < len(monster_imgs) else None) for i in range(3)]
current_monster_idx = 0
monster = monsters[current_monster_idx]
bonus = Bonus(bonus_img)
bonus.timer = BONUS_RESPAWN_INTERVAL * 0.5  # начнёт появляться скоро

# -------------- Game state --------------
MENU, GAME, PAUSE, GAME_OVER = "MENU","GAME","PAUSE","GAME_OVER"
state = MENU

score = 0
game_time = 0.0
hit_flash_timer = 0.0
player_damaged = False

# -------------- Вспомогательные функции --------------
def lerp(a, b, t):
    return a + (b - a) * t

def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))

def draw_texture(img, pos, scale=1.0, tint=None):
    """Draw image with scale and optional tint color (pygame doesn't have easy tinting; we do simple)."""
    if img:
        w = int(img.get_width() * scale)
        h = int(img.get_height() * scale)
        surf = pygame.transform.smoothscale(img, (w, h))
        if tint is not None:
            # apply tint by multiplying alpha onto a copy
            tinted = surf.copy()
            tinted.fill(tint, special_flags=pygame.BLEND_RGB_MULT)
            screen.blit(tinted, pos)
        else:
            screen.blit(surf, pos)
    else:
        # placeholder rectangle
        w = int(60 * scale)
        h = int(100 * scale)
        pygame.draw.rect(screen, (120,120,120), pygame.Rect(pos[0], pos[1], w, h))

def rect_from_pos_size(pos, size):
    return pygame.Rect(int(pos[0]), int(pos[1]), int(size[0]), int(size[1]))

# -------------- Основной цикл --------------
running = True
clock = pygame.time.Clock()

while running:
    dt = clock.tick(FPS) / 1000.0
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            running = False
        elif ev.type == pygame.KEYDOWN:
            if ev.key == pygame.K_RETURN and state == MENU:
                state = GAME
                # reset some values
                player = Player()
                monsters = [Monster(i, monster_imgs[i] if i < len(monster_imgs) else None) for i in range(3)]
                current_monster_idx = 0
                monster = monsters[current_monster_idx]
                bonus = Bonus(bonus_img)
                score = 0
                game_time = 0.0
                hit_flash_timer = 0.0
                player_damaged = False
            elif ev.key == pygame.K_p and state == GAME:
                state = PAUSE
            elif ev.key == pygame.K_p and state == PAUSE:
                state = GAME
            elif ev.key == pygame.K_m:
                # back to menu
                state = MENU
            elif ev.key == pygame.K_q:
                state = GAME_OVER
            elif ev.key == pygame.K_SPACE and state == GAME:
                # attack attempt handled in update
                pass

    # ---------- Game update ----------
    if state == GAME:
        game_time += dt

        keys = pygame.key.get_pressed()
        # Movement (arrow keys)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            player.pos.x += player.speed * dt
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            player.pos.x -= player.speed * dt
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            player.pos.y -= player.speed * dt
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            player.pos.y += player.speed * dt

        # clamp inside screen
        pw, ph = player.size
        player.pos.x = clamp(player.pos.x, 0, SCREEN_W - pw)
        player.pos.y = clamp(player.pos.y, 0, SCREEN_H - ph)

        # timers
        if hit_flash_timer > 0:
            hit_flash_timer -= dt
        if player.damage_timer > 0:
            player.damage_timer -= dt
            if player.damage_timer <= PLAYER_DAMAGE_INTERVAL - 0.3:
                player_damaged = False

        if player.attack_cooldown > 0:
            player.attack_cooldown -= dt

        # bonus spawn logic
        bonus.timer -= dt
        if not bonus.active and bonus.timer <= 0.0:
            bonus.pos = pygame.Vector2(random.randint(0, SCREEN_W - bonus.size[0]), random.randint(0, SCREEN_H - bonus.size[1]))
            bonus.active = True
            bonus.timer = BONUS_RESPAWN_INTERVAL

        # monster logic (chase player)
        if monster.health > 0:
            dir_vec = player.pos - monster.pos
            dist = dir_vec.length()
            if dist != 0:
                dir_vec = dir_vec.normalize()
                monster.pos += dir_vec * monster.speed * dt
        else:
            monster.respawn_timer -= dt
            if monster.respawn_timer <= 0:
                current_monster_idx = (current_monster_idx + 1) % len(monsters)
                monster = monsters[current_monster_idx]
                monster.pos = pygame.Vector2(random.randint(0, SCREEN_W), random.randint(0, SCREEN_H))
                monster.health = monster.max_health
                monster.respawn_timer = 0.0

        # collision rectangles
        player_rect = rect_from_pos_size(player.pos, player.size)
        monster_rect = rect_from_pos_size(monster.pos, monster.size)

        # monster damages player on contact (with damage interval)
        if monster.health > 0 and player_rect.colliderect(monster_rect):
            if player.damage_timer <= 0.0:
                player.health -= 5
                player.damage_timer = PLAYER_DAMAGE_INTERVAL
                player_damaged = True
        # update damage timer visual reset handled above

        # attack (space)
        if keys[pygame.K_SPACE] and player.attack_cooldown <= 0.0:
            if monster.health > 0 and player_rect.colliderect(monster_rect):
                monster.health -= 25
                hit_flash_timer = 0.2
                if monster.health <= 0:
                    monster.respawn_timer = MONSTER_RESPAWN_TIME
                    score += 10
            player.attack_cooldown = PLAYER_ATTACK_COOLDOWN

        # bonus pickup
        if bonus.active:
            bonus_rect = rect_from_pos_size(bonus.pos, bonus.size)
            if player_rect.colliderect(bonus_rect):
                player.health += 20
                if player.health > PLAYER_HEALTH:
                    player.health = PLAYER_HEALTH
                bonus.active = False
                bonus.timer = BONUS_RESPAWN_INTERVAL

        # game over check
        if player.health <= 0:
            state = GAME_OVER

    # ---------- Рендер ----------
    screen.fill((200, 200, 200))
    # background
    if bg_img:
        screen.blit(bg_img, (0,0))
    else:
        screen.fill((100,150,100))  # placeholder greenish

    if state == MENU:
        txt = font_big.render("Game Menu. Press ENTER to start", True, (0,0,0))
        screen.blit(txt, (SCREEN_W//3, SCREEN_H//3))
        txt2 = font_small.render("Press Q to simulate Game Over", True, (0,0,0))
        screen.blit(txt2, (SCREEN_W//3, SCREEN_H//3 + 40))

    elif state == GAME or state == PAUSE:
        # UI text
        ui_text = font_small.render("Game in progress. Press P to pause. SPACE to attack", True, (0,0,0))
        screen.blit(ui_text, (SCREEN_W//3, 10))

        # draw player (tint red if damaged)
        p_tint = (255,255,255) if not player_damaged else (255,120,120)
        draw_texture(player_img, (player.pos.x, player.pos.y), player.scale, None if not player_damaged else (255,120,120))

        # draw monster if alive
        if monster.health > 0:
            m_tint = None
            if hit_flash_timer > 0:
                m_tint = (255,100,100)
            draw_texture(monster.image, (monster.pos.x, monster.pos.y), monster.scale, m_tint)
            # health text
            mh_text = font_small.render(str(monster.health), True, (200,0,0))
            screen.blit(mh_text, (monster.pos.x, monster.pos.y - 22))
        else:
            # if dead maybe draw nothing or a fading corpse (simple nothing)
            pass

        # draw bonus
        if bonus.active:
            draw_texture(bonus.image, (bonus.pos.x, bonus.pos.y), bonus.scale)

        # HUD
        pygame.draw.rect(screen, (50,50,50,180), (10,10,250,80))
        pygame.draw.rect(screen, (0,0,0), (10,10,250,80), 1)
        hp_text = font_small.render(f"HP: {player.health}", True, (200,0,0))
        screen.blit(hp_text, (20,20))
        time_text = font_small.render(f"Time: {game_time:.1f} s", True, (0,0,0))
        screen.blit(time_text, (20,40))
        score_text = font_small.render(f"Score: {score}", True, (0,0,100))
        screen.blit(score_text, (20,60))

        if state == PAUSE:
            pause_txt = font_big.render("Paused. Press P to continue", True, (80,80,80))
            screen.blit(pause_txt, (SCREEN_W//3, SCREEN_H//3))

    elif state == GAME_OVER:
        go_text = font_big.render("Game Over. Press M to return to menu", True, (200,0,0))
        screen.blit(go_text, (SCREEN_W//3, SCREEN_H//3))

    # red flash if damaged
    if player_damaged:
        overlay = pygame.Surface((SCREEN_W, SCREEN_H), pygame.SRCALPHA)
        overlay.fill((255,0,0, int(0.2 * 255)))
        screen.blit(overlay, (0,0))

    pygame.display.flip()

pygame.quit()
sys.exit()
