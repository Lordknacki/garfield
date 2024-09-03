import pygame
import random
import sys
import os

# Fonctions utilitaires pour la gestion des scores
def load_scores():
    """Charge les scores depuis un fichier."""
    if not os.path.exists('scores.txt'):
        return []
    with open('scores.txt', 'r') as file:
        scores = file.read().splitlines()
    return [int(score) for score in scores]

def save_score(new_score):
    """Enregistre un nouveau score dans le fichier de scores."""
    scores = load_scores()
    scores.append(new_score)
    scores = sorted(scores, reverse=True)[:10]  # Garde uniquement les 10 meilleurs scores
    with open('scores.txt', 'w') as file:
        for score in scores:
            file.write(f"{score}\n")

def display_leaderboard(screen, scores):
    """Affiche le leaderboard à l'écran."""
    font = pygame.font.SysFont("monospace", 24)
    y = 100
    for index, score in enumerate(scores):
        text = font.render(f"{index + 1}. Score: {score}", True, (255, 255, 255))
        screen.blit(text, (100, y))
        y += 30

# Initialisation de Pygame
pygame.init()

# Configuration de l'écran
infoObject = pygame.display.Info()
screen_width, screen_height = infoObject.current_w, infoObject.current_h
screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
clock = pygame.time.Clock()

# Chargement des ressources
background_image = pygame.image.load('img/background.png')
player_image = pygame.image.load('img/player.png')
good_item_image = pygame.image.load('img/good_item.png')
bad_item_image = pygame.image.load('img/bad_item.png')
worse_item_image = pygame.image.load('img/worse_item.png')
cursor_image = pygame.image.load('img/custom_cursor.png')

# Variables du jeu
player_size = player_image.get_width()
player_pos = [screen_width // 2, screen_height - player_image.get_height()]
items = []
item_size = good_item_image.get_width()
fall_speed = 10
score = 0
max_items = 40
special_item_added = False

# Fonts pour l'affichage
font = pygame.font.SysFont("monospace", 35)
end_font = pygame.font.SysFont("monospace", 100)

# Masquer le curseur standard de la souris
pygame.mouse.set_visible(False)

# Gestion du temps
start_time = pygame.time.get_ticks()
game_duration = 60000  # 1 minute en millisecondes
last_increase_time = start_time

def drop_items(time_left):
    global special_item_added
    if time_left > 2:
        if len(items) < max_items and random.randint(1, 10) == 1:
            draw = random.randint(1, 100)
            if draw <= 10:
                item_image = worse_item_image
                points = -3
            elif draw <= 25:
                item_image = bad_item_image
                points = -1
            else:
                item_image = good_item_image
                points = 1
            new_pos = random.randrange(0, screen_width - item_size)
            item_pos = [new_pos, 0, item_image, points]
            items.append(item_pos)
    elif time_left == 2 and not special_item_added:
        item_image = good_item_image  # Objet spécial
        points = 5
        new_pos = random.randrange(0, screen_width - item_size)
        special_item = [new_pos, 0, item_image, points]
        items.append(special_item)
        special_item_added = True

def draw_items():
    """Dessine les objets sur l'écran."""
    for item in items:
        screen.blit(item[2], (item[0], item[1]))

def update_item_positions():
    """Met à jour la position des objets tombants."""
    global items
    items = [item for item in items if item[1] <= screen_height]
    for item in items:
        item[1] += fall_speed

def collision_check():
    """Vérifie les collisions entre le joueur et les objets."""
    global score
    player_rect = pygame.Rect(player_pos[0], player_pos[1], player_size, player_image.get_height())
    for idx in range(len(items) - 1, -1, -1):
        item = items[idx]
        item_rect = pygame.Rect(item[0], item[1], item_size, item_size)
        if player_rect.colliderect(item_rect):
            score += item[3]
            items.pop(idx)

# Boucle principale du jeu
game_over = False
while not game_over:
    current_time = pygame.time.get_ticks()
    time_left = game_duration // 1000 - (current_time - start_time) // 1000
    if current_time - start_time >= game_duration:
        game_over = True
        save_score(score)
        screen.fill((0, 0, 0))
        scores = load_scores()
        display_leaderboard(screen, scores)
        pygame.display.update()
        pygame.time.wait(5000)
        pygame.quit()
        sys.exit()

    if current_time - last_increase_time >= 5000:
        fall_speed += 1
        last_increase_time = current_time

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            pygame.quit()
            sys.exit()

    mouse_x, mouse_y = pygame.mouse.get_pos()
    player_pos[0] = max(0, min(mouse_x, screen_width - player_size))

    screen.blit(background_image, (0, 0))
    drop_items(time_left)
    update_item_positions()
    collision_check()
    draw_items()
    screen.blit(player_image, (player_pos[0], player_pos[1]))
    screen.blit(font.render(f"Score: {score}", True, (0, 0, 0)), (20, 20))
    timer_text = font.render(f"Time: {time_left}s", True, (0, 0, 0))
    screen.blit(timer_text, (screen_width - timer_text.get_width() - 20, 20))

    screen.blit(cursor_image, (mouse_x, mouse_y))

    pygame.display.update()
    clock.tick(30)

# Nettoyer et quitter Pygame proprement
pygame.quit()
sys.exit()
