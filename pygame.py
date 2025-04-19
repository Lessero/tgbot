import pygame
import random
import sys

# Initialize pygame
pygame.init()
import pygame
import random
import sys

# Initialize pygame
pygame.init()

# Screen dimensions
screen_width = 800
screen_height = 600

# Colors
colors = {
    "space": (0, 0, 50),
    "jungle": (34, 139, 34),
    "underwater": (0, 105, 148),
    "player": (255, 255, 255),
    "target": (255, 215, 0),
    "obstacle": (255, 0, 0),
}

# Themes
themes = ["space", "jungle", "underwater"]
current_theme = random.choice(themes)

# Initialize screen
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Themed Game with Lives")

# Clock
clock = pygame.time.Clock()

# Player attributes
player_size = 50
player_pos = [screen_width // 2, screen_height - 2 * player_size]
player_speed = 10

# Target attributes
target_size = 30
target_pos = [random.randint(0, screen_width - target_size), random.randint(0, screen_height - target_size)]

# Obstacle attributes
obstacle_size = 50
obstacle_pos = [random.randint(0, screen_width - obstacle_size), 0]
obstacle_speed = 5

# Game variables
score = 0
lives = 3
game_over = False

def detect_collision(player_pos, obj_pos, obj_size):
    px, py = player_pos
    ox, oy = obj_pos
    if (ox < px < ox + obj_size or ox < px + player_size < ox + obj_size) and \
       (oy < py < oy + obj_size or oy < py + player_size < oy + obj_size):
        return True
    return False

def draw_text(text, size, color, x, y):
    font = pygame.font.Font(None, size)
    label = font.render(text, True, color)
    screen.blit(label, (x, y))

# Game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT] and player_pos[0] > 0:
        player_pos[0] -= player_speed
    if keys[pygame.K_RIGHT] and player_pos[0] < screen_width - player_size:
        player_pos[0] += player_speed
    if keys[pygame.K_UP] and player_pos[1] > 0:
        player_pos[1] -= player_speed
    if keys[pygame.K_DOWN] and player_pos[1] < screen_height - player_size:
        player_pos[1] += player_speed

    screen.fill(colors[current_theme])

    # Draw player, target, and obstacle
    pygame.draw.rect(screen, colors["player"], (*player_pos, player_size, player_size))
    pygame.draw.rect(screen, colors["target"], (*target_pos, target_size, target_size))
    pygame.draw.rect(screen, colors["obstacle"], (*obstacle_pos, obstacle_size, obstacle_size))

    # Move obstacle
    obstacle_pos[1] += obstacle_speed
    if obstacle_pos[1] > screen_height:
        obstacle_pos = [random.randint(0, screen_width - obstacle_size), 0]

    # Check collisions
    if detect_collision(player_pos, target_pos, target_size):
        score += 1
        target_pos = [random.randint(0, screen_width - target_size), random.randint(0, screen_height - target_size)]

    if detect_collision(player_pos, obstacle_pos, obstacle_size):
        lives -= 1
        obstacle_pos = [random.randint(0, screen_width - obstacle_size), 0]
        if lives == 0:
            game_over = True

    # Display score and lives
    draw_text(f"Score: {score}", 36, (255, 255, 255), 10, 10)
    draw_text(f"Lives: {lives}", 36, (255, 255, 255), 10, 50)

    if game_over:
        screen.fill((0, 0, 0))
        draw_text("GAME OVER", 72, (255, 0, 0), screen_width // 2 - 150, screen_height // 2 - 50)
        draw_text(f"Final Score: {score}", 48, (255, 255, 255), screen_width // 2 - 150, screen_height // 2 + 50)
        pygame.display.update()
        pygame.time.wait(3000)
        pygame.quit()
        sys.exit()

    pygame.display.update()
    clock.tick(30)
