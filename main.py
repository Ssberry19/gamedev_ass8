import pygame
import random
import time

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Screen dimensions
screen_width, screen_height = 800, 600
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('2D Game Level')

# Level Definitions (Basic and Advanced Levels)
levels = {
    1: {
        'level_data': [
            'WWWWWWWWWWWWW',
            'WIIIFFFIFIIFW',
            'WFFFFIFFFFFFW',
            'WIFFIIFFIIIFW',
            'WFFFFIFFFFFFW',
            'WIIIFFFIFIIFW',
            'WWWWWWWWWWWWW',
        ],
        'enemies': [[2, 2], [5, 5]],
        'enemy_speed': 1,
        'enemy_move_interval': 10,
    },
    2: {
        'level_data': [
            'WWWWWWWWWWWWWWWWWWWW',
            'WFFFFFFFFFFFFFFFFFFW',
            'WIWFWFWFFWWFIWFWFWIW',
            'WFFFFFFFFFFFFFFFFFFW',
            'WFWFWIWFFWWIFWFWFWFW',
            'WFWFWFWIFWWFFWFWFWFW',
            'WFWFWFWFFWWFIWFWFWFW',
            'WFWFWFWFFWWFFWFWFWFW',
            'WFFFFIFFFFFIFFFFFFFW',
            'WWWWWWWWWWWWWWWWWWWW',
        ],
        'enemies': [[2, 3], [3, 5], [8, 8], [8, 15]],
        'enemy_speed': 2,
        'enemy_move_interval': 5,
    },

    3: {
        'level_data': [
            'WWWWWWWWWWWWWWWWWWWWWWWWWWWWWW',
            'WFFFFFFFFFFFFFFFIFFFFFWFIFFFWW',
            'WFFFFWWWWWWWWWWWWFFFIWFFFIWFFW',
            'WFFIFWFFFFFFFFFWFFFFWWFFFFFFWW',
            'WFFFFFFFWWWWWFFFFFFFFIIFFFFWWW',
            'WFFFFFFFFFFFFFFWFFFFFWWWIFFFFW',
            'WFWFFFIFFWFFFFFFWFFFFWFFFIFFFW',
            'WFFFFFFFWWFFFFFFWFFFFFFFFFFFFW',
            'WFFFFFFFFFFIFFFFFFFFIFFFFFFWWW',
            'WFFFWFFFFFFFFFFFFIWFFIFFFFFFFW',
            'WFFWFFFFFFFWWWFFFFFFIWWFFFIFFW',
            'WFFFFFFFFIWFFFFIFFFFFWFFFFFFFW',
            'WIFFWWFFFFFFFFFFWFFFFFFFFFFFFW',
            'WFFFFWFFFFFFFIFFFFFFIWWWFFFFWW',
            'WWWWWWWWWWWWWWWWWWWWWWWWWWWWWW',

        ],
        'enemies': [[1, 4], [2, 6], [4, 2], [6, 5], [7, 3], [3, 7], [6, 11], [8, 4], [10,15], [3,25], [5,18], [13,27], [12,20]],
        'enemy_speed': 3,
        'enemy_move_interval': 3,
    },

}

tile_size = 40

# Load textures for tiles
wall_texture = pygame.image.load('floor.jpg')
floor_texture = pygame.image.load('wall.png')
item_texture = pygame.image.load('item.png')
enemy_texture = pygame.image.load('enemy.png')

wall_texture = pygame.transform.scale(wall_texture, (tile_size, tile_size))
floor_texture = pygame.transform.scale(floor_texture, (tile_size, tile_size))
item_texture = pygame.transform.scale(item_texture, (tile_size, tile_size))
enemy_texture = pygame.transform.scale(enemy_texture, (tile_size, tile_size))

player_texture = pygame.image.load('player.png')
player_texture = pygame.transform.scale(player_texture, (tile_size, tile_size))


# Player settings
player_pos = [1, 1]
tile_size = 40
score = 0
health = 100
current_level = 1

# Enemy settings
enemies = []
enemy_speed = 0
enemy_move_counter = 0
enemy_move_interval = 0

# Camera settings
camera_x, camera_y = 0, 0
camera_width = screen_width // tile_size
camera_height = screen_height // tile_size

# Sound effects
item_collect_sound = pygame.mixer.Sound("collect.wav")  # Replace with your sound file
enemy_collision_sound = pygame.mixer.Sound("enemy.wav")  # Replace with your sound file

# Background Music
pygame.mixer.music.load("background2.wav")  # Replace with your music file
pygame.mixer.music.play(-1)

# Font for text
font = pygame.font.Font(None, 36)

# Function to load level data
def load_level():
    global level, enemies, enemy_speed, enemy_move_interval, player_pos, total_items
    level_data_string = levels[current_level]['level_data']
    # Replace any undefined tile with 'F' (floor) to avoid invalid behavior
    level_data = [list(row.replace(' ', 'F')) for row in level_data_string]
    enemies = levels[current_level]['enemies']
    enemy_speed = levels[current_level]['enemy_speed']
    enemy_move_interval = levels[current_level]['enemy_move_interval']
    total_items = sum(row.count('I') for row in level_data)  # Calculate total items in the level
    level = level_data
    player_pos = [1, 1]

# Render the level on screen
# Function to render the level with exposure effect on the floor
def render_level(level, camera_x, camera_y):
    for y, row in enumerate(level):
        for x, tile in enumerate(row):
            if y >= camera_y and y < camera_y + camera_height and x >= camera_x and x < camera_x + camera_width:
                screen_x = (x - camera_x) * tile_size
                screen_y = (y - camera_y) * tile_size

                # Draw textures based on the tile type
                if tile == 'W':
                    screen.blit(wall_texture, (screen_x, screen_y))
                elif tile == 'F':
                    # Apply exposure effect to floor texture
                    # Create a surface for exposure effect (semi-transparent black overlay)
                    exposure_overlay = pygame.Surface((tile_size, tile_size))
                    exposure_overlay.fill((0, 0, 0))  # Black color overlay
                    exposure_overlay.set_alpha(50)  # Adjust the alpha for exposure effect (0-255)

                    screen.blit(floor_texture, (screen_x, screen_y))
                    screen.blit(exposure_overlay, (screen_x, screen_y))  # Add the overlay
                elif tile == 'I':
                    screen.blit(item_texture, (screen_x, screen_y))


# Render player character on screen
def render_player(position, camera_x, camera_y):
    screen_x = (position[1] - camera_x) * tile_size
    screen_y = (position[0] - camera_y) * tile_size
    screen.blit(player_texture, (screen_x, screen_y))

# Check for collisions with walls and enemies
def check_collision(pos):
    # Ensure the position is within bounds before accessing the level
    if pos[0] < 0 or pos[0] >= len(level) or pos[1] < 0 or pos[1] >= len(level[0]):
        return False  # If out of bounds, treat it as a collision (no movement allowed)

    tile = level[pos[0]][pos[1]]
    if tile == 'W':
        return False  # Collision with a wall
    for enemy in enemies:
        if pos == enemy:
            return "enemy"  # Collision with an enemy
    return True  # No collision

# Collect items and increase score
def collect_item(position):
    global score
    if level[position[0]][position[1]] == 'I':
        score += 1
        level[position[0]][position[1]] = 'F'  # Replace the item with a floor tile
        item_collect_sound.play()

# Move enemies randomly
def move_enemies():
    global enemies
    for i, enemy in enumerate(enemies):
        dx, dy = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
        new_enemy_pos = [enemy[0] + dy, enemy[1] + dx]
        if 0 <= new_enemy_pos[0] < len(level) and 0 <= new_enemy_pos[1] < len(level[0]) and level[new_enemy_pos[0]][new_enemy_pos[1]] != 'W':
            enemies[i] = new_enemy_pos

# Render enemies on screen
def render_enemies(enemies, camera_x, camera_y):
    for enemy in enemies:
        screen_x = (enemy[1] - camera_x) * tile_size
        screen_y = (enemy[0] - camera_y) * tile_size
        screen.blit(enemy_texture, (screen_x, screen_y))


# Function to display a message on the screen
def display_message(message, color, y_offset=0):
    text = font.render(message, True, color)
    text_rect = text.get_rect(center=(screen_width // 2, screen_height // 2 + y_offset))
    screen.blit(text, text_rect)

# Game loop
running = True
game_over = False
level_complete = False
start_time = time.time()
time_limit = 60
clock = pygame.time.Clock()
FPS = 30
total_items = 0  # Total items to collect in the level

# Load the initial level
load_level()

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    new_player_pos = player_pos[:]

    if keys[pygame.K_w]:
        new_player_pos[0] -= 1
    if keys[pygame.K_s]:
        new_player_pos[0] += 1
    if keys[pygame.K_a]:
        new_player_pos[1] -= 1
    if keys[pygame.K_d]:
        new_player_pos[1] += 1

    if new_player_pos != player_pos:
        collision_type = check_collision(new_player_pos)
        if collision_type:
            if collision_type is True:
                player_pos = new_player_pos
                collect_item(player_pos)
            elif collision_type == "enemy":
                health -= 10
                enemy_collision_sound.play()
                if health <= 0:
                    game_over = True

    enemy_move_counter += 1
    if enemy_move_counter >= enemy_move_interval:
        move_enemies()
        enemy_move_counter = 0

    camera_x = max(0, min(player_pos[1] - camera_width // 2, len(level[0]) - camera_width))
    camera_y = max(0, min(player_pos[0] - camera_height // 2, len(level) - camera_height))

    screen.fill((0, 0, 0))
    render_level(level, camera_x, camera_y)
    render_player(player_pos, camera_x, camera_y)
    render_enemies(enemies, camera_x, camera_y)

    # Display score and health
    score_text = font.render(f'Score: {score}', True, (255, 255, 255))
    health_text = font.render(f'Health: {health}', True, (255, 255, 255))
    screen.blit(score_text, (10, 10))
    screen.blit(health_text, (10, 50))

    # Check if all items are collected
    if score >= total_items:
        level_complete = True
        if current_level == 1:
            display_message("Level 1 Complete!", (0, 255, 0))
            display_message("Press Enter to continue to Level 2, R to Restart, ESC to Quit.", (255, 255, 255), 50)
        elif current_level == 2:
            display_message("Level 2 Complete!", (0, 255, 0))
            display_message("Press Enter to continue to Level 3, R to Restart, ESC to Quit.", (255, 255, 255), 50)
        elif current_level == 3:
            display_message("You Won!", (0, 255, 0))
            display_message("Press R to Restart, ESC to Quit.", (255, 255, 255), 50)

        pygame.display.flip()
        pygame.time.delay(500)

        # Wait for the player to press a key to continue, restart, or quit
        waiting_for_input = True
        while waiting_for_input:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    waiting_for_input = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:  # Press Enter to continue to the next level
                        if current_level < 3:
                            current_level += 1
                            load_level()  # Load the next level
                            health = 100
                            score = 0  # Reset score for the next level
                            waiting_for_input = False
                    elif event.key == pygame.K_r:  # Press R to restart the current level
                        load_level()  # Reload the current level
                        health = 100
                        score = 0  # Reset score
                        level_complete = False
                        waiting_for_input = False
                    elif event.key == pygame.K_ESCAPE:  # Press Escape to quit the game
                        running = False
                        waiting_for_input = False

    if game_over:
        display_message("Game Over!", (255, 0, 0))
        display_message("Press R to Restart, ESC to Quit.", (255, 255, 255), 50)
        pygame.display.flip()
        pygame.time.delay(500)

        # Wait for the player to press a key to restart or quit
        waiting_for_input = True
        while waiting_for_input:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    waiting_for_input = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:  # Press R to restart the current level
                        load_level()  # Reload the current level
                        health = 100
                        score = 0  # Reset score
                        game_over = False
                        waiting_for_input = False
                    elif event.key == pygame.K_ESCAPE:  # Press Escape to quit the game
                        running = False
                        waiting_for_input = False

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()