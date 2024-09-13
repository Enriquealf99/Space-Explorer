import pygame
import random
import pandas as pd
import scores as scores
# Initialize Pygame
pygame.init()

# Screen dimensions
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Explorer")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Load and resize images
player_img = pygame.image.load("spaceship.png").convert_alpha()
player_img = pygame.transform.scale(player_img, (50, 75))  # Resize spaceship to 50x75

enemy_img = pygame.image.load("asteroid.png").convert()
enemy_img.set_colorkey(WHITE)
enemy_img = pygame.transform.scale(enemy_img, (50, 50))  # Resize asteroid to 50x50

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = player_img
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.center = (WIDTH // 2, HEIGHT - 50)
        self.speed = 5
        self.lives = 3  # Player starts with 3 lives

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += self.speed
        if keys[pygame.K_UP] and self.rect.top > 0:
            self.rect.y -= self.speed
        if keys[pygame.K_DOWN] and self.rect.bottom < HEIGHT:
            self.rect.y += self.speed

# Enemy class
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = enemy_img
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = random.randint(0, WIDTH - self.rect.width)
        self.rect.y = random.randint(-100, -40)
        self.speedy = random.randint(2, 6)

    def update(self):
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT:
            self.rect.x = random.randint(0, WIDTH - self.rect.width)
            self.rect.y = random.randint(-100, -40)
            self.speedy = random.randint(2, 6)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((5, 10))  # Size of the bullet
        self.image.fill(WHITE)  # Color of the bullet
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.top = y
        self.speedy = -10  # Speed at which the bullet moves (upwards)

    def update(self):
        # Move the bullet upwards
        self.rect.y += self.speedy
        # Remove the bullet if it moves off the top of the screen
        if self.rect.bottom < 0:
            self.kill()


# Function to display lives
def draw_lives(surface, lives):
    font = pygame.font.Font(None, 36)
    lives_text = font.render(f"Lives: {lives}", True, WHITE)
    surface.blit(lives_text, (WIDTH - 150, 10))

# Function to display "Game Over" when the player runs out of lives
def game_over(screen):
    font = pygame.font.Font(None, 100)
    game_over_text = font.render("GAME OVER", True, RED)
    screen.blit(game_over_text, (WIDTH // 2 - 200, HEIGHT // 2 - 50))
    scores.update_scores(player_name, score)  
    smaller_font = pygame.font.Font(None, 50)
    final_score_text = smaller_font.render(f"Final Score: {score}", True, RED)
    screen.blit(final_score_text, (WIDTH // 2 - 150, HEIGHT // 2 + 50))  
    
    scores.print_scores()
    pygame.display.flip()
    pygame.time.wait(3000)

def get_player_name(screen):
    font = pygame.font.Font(None, 50)
    player_name = ''  # Start with an empty name
    input_active = True

    while input_active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()  # Close the game window properly
                exit()  # Exit the entire program
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    input_active = False  # Stop input on Enter
                elif event.key == pygame.K_BACKSPACE:
                    player_name = player_name[:-1]  # Remove the last character
                else:
                    if len(player_name) < 10:  # Limit the player name length
                        player_name += event.unicode  # Add typed character to name

        # Render player name
        screen.fill(BLACK)  # Clear the screen
        prompt_text = font.render("Enter Your Name: " + player_name, True, WHITE)
        screen.blit(prompt_text, (WIDTH // 2 - 200, HEIGHT // 2 - 25))

        pygame.display.flip()

    return player_name  # Return the final player name after Enter is pressed

# Function to spawn a new enemy with increased difficulty
def spawn_enemy(speed_increase):
    enemy = Enemy()
    enemy.speedy += speed_increase  # Increase the speed based on difficulty
    return enemy


# Main game loop
def main_game_loop():
    global score
    score = 0  # Initialize the score
    global player_name 
    palyer_name = get_player_name(screen)  # Get player name before starting

    if player_name is None:
        return  # If the player quits while entering name, exit the game

    player = Player()
    all_sprites = pygame.sprite.Group()
    all_sprites.add(player)
    enemies = pygame.sprite.Group()
    bullets = pygame.sprite.Group()

    # Create initial enemies
    for i in range(8):
        enemy = spawn_enemy(0)  # Initial speed, no increase yet
        all_sprites.add(enemy)
        enemies.add(enemy)

    # Game variables
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)  # Font for displaying score
    difficulty_timer = pygame.time.get_ticks()  # Start the difficulty timer
    difficulty_interval = 15000  # Increase difficulty every 15 seconds
    speed_increase = 1  # Amount to increase speed each difficulty increment

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bullet = Bullet(player.rect.centerx, player.rect.top)
                    all_sprites.add(bullet)
                    bullets.add(bullet)

        all_sprites.update()

        # Pixel-perfect collision detection between player and enemies
        collisions = pygame.sprite.spritecollide(player, enemies, True, pygame.sprite.collide_mask)
        for collision in collisions:
            player.lives -= 1  # Reduce player's lives by 1
            enemy = spawn_enemy(speed_increase)  # Spawn a new enemy with increased speed
            all_sprites.add(enemy)
            enemies.add(enemy)
            if player.lives <= 0:
                game_over(screen, player_name)
                running = False

        hits = pygame.sprite.groupcollide(enemies, bullets, True, True)
        for hit in hits:
            score += 10
            enemy = spawn_enemy(speed_increase)  # Spawn a new enemy with increased speed
            all_sprites.add(enemy)
            enemies.add(enemy)

        # Check if it's time to increase difficulty
        current_time = pygame.time.get_ticks()
        if current_time - difficulty_timer > difficulty_interval:
            speed_increase += 1  # Increase enemy speed
            difficulty_timer = current_time  # Reset the timer
            print(f"Difficulty increased! Enemy speed increased to {speed_increase}")

        # Drawing on the screen
        screen.fill(BLACK)
        all_sprites.draw(screen)
        score_text = font.render(f"Score: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))
        draw_lives(screen, player.lives)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
