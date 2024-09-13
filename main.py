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
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Load and resize images
player_img = pygame.image.load("spaceship.png").convert_alpha()
player_img = pygame.transform.scale(player_img, (50, 75))  # Resize spaceship to 50x75

enemy_img = pygame.image.load("asteroid.png").convert()
enemy_img.set_colorkey(WHITE)
enemy_img = pygame.transform.scale(enemy_img, (80, 80))  # Resize asteroid to 50x50


bullet_upgrade_img = pygame.image.load("bullet_upgrade.png").convert()
bullet_upgrade_img.set_colorkey(WHITE)
bullet_upgrade_img = pygame.transform.scale(bullet_upgrade_img, (50, 50))

bullet_speed_upgrade_img = pygame.image.load("bullet_speed_upgrade.png").convert()
bullet_speed_upgrade_img.set_colorkey(WHITE)
bullet_speed_upgrade_img = pygame.transform.scale(bullet_speed_upgrade_img, (50, 50))

# Player class
class Player(pygame.sprite.Sprite):
    def __init__(self, all_sprites, bullets):
        super().__init__()
        self.image = player_img
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.center = (WIDTH // 2, HEIGHT - 50)
        self.speed = 5
        self.lives = 3  # Player starts with 3 lives
        self.shoot_delay = 500  # Set the shooting interval in milliseconds (500 ms = 0.5 seconds)
        self.last_shot = pygame.time.get_ticks()  # Track when the player last shot a bullet
        self.all_sprites = all_sprites  # Store reference to all_sprites group
        self.bullets = bullets  # Store reference to bullets group
        self.bullet_count = 1  # Number of bullets shot at once

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
        self.shoot()

    def shoot(self):
        now = pygame.time.get_ticks()

        # If enough time has passed since the last shot, shoot again
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now  # Reset the last shot timer

            # Spread bullets horizontally based on bullet_count
            bullet_spacing = 10  # Distance between bullets
            start_pos = self.rect.centerx - ((self.bullet_count - 1) * bullet_spacing) // 2

            # Shoot multiple bullets spread out horizontally
            for i in range(self.bullet_count):
                bullet = Bullet(start_pos + i * bullet_spacing, self.rect.top)
                self.all_sprites.add(bullet)
                self.bullets.add(bullet)
    
    def increase_bullet_count(self):
        self.bullet_count += 1  # Increase the number of bullets fired

    def increase_speed(self):
        self.shoot_delay -= 50 # decrease the delay between bullets are fired
        self.speed += 0.5 # Increment the speed

# Enemy class
class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = enemy_img
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.x = random.randint(0, WIDTH - self.rect.width)
        self.rect.y = random.randint(-100, -40)
        self.health = 1

        # Random vertical and horizontal speed for diagonal movement
        self.speedy = random.randint(2, 6)
        self.speedx = random.choice([0, random.randint(-3, 3)])  # Randomize horizontal speed

    def update(self):
        self.rect.y += self.speedy
        self.rect.x += self.speedx  # Move horizontally for diagonal movement

        # Bounce off the sides if the asteroid hits the screen edges
        if self.rect.left <= 0 or self.rect.right >= WIDTH:
            self.speedx = -self.speedx  # Reverse horizontal direction

        # If the asteroid moves off the bottom of the screen, reset its position
        if self.rect.top > HEIGHT:
            self.rect.x = random.randint(0, WIDTH - self.rect.width)
            self.rect.y = random.randint(-100, -40)
            self.speedy = random.randint(2, 6)
            self.speedx = random.choice([0, random.randint(-3, 3)])  # Randomize horizontal speed again
    
    def take_damage(self, damage):
        self.health -= damage  # Reduce health by the given damage amount
        if self.health <= 0:
            self.kill()  # Destroy asteroid if health reaches 0

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((5, 10))  # Size of the bullet
        self.image.fill(GREEN)  # Color of the bullet
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.centerx = x
        self.rect.top = y
        self.speedy = -10  # Speed at which the bullet moves (upwards)

    def update(self):
        # Move the bullet upwards
        self.rect.y += self.speedy
        # Remove the bullet if it moves off the top of the screen
        if self.rect.bottom < 0:
            self.kill()

class PowerUp(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = bullet_upgrade_img
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WIDTH - self.rect.width)
        self.rect.y = random.randint(-100, -40)
        self.speedy = 3  

    def update(self):
        self.rect.y += self.speedy
        # Remove the power-up if it moves off the screen
        if self.rect.top > HEIGHT:
            self.kill()

class SpeedUp(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = bullet_speed_upgrade_img
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, WIDTH - self.rect.width)
        self.rect.y = random.randint(-100, -40)
        self.speedy = 3  

    def update(self):
        self.rect.y += self.speedy
        # Remove the speed-up if it moves off the screen
        if self.rect.top > HEIGHT:
            self.kill()


# Function to display lives

def draw_lives(surface, lives):
    font = pygame.font.Font(None, 36)
    lives_text = font.render(f"Lives: {lives}", True, WHITE)
    surface.blit(lives_text, (WIDTH - 150, 10))

# Function to display "Game Over" when the player runs out of lives
def game_over(screen, player_name):
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
def spawn_enemy(speed_increase, health_increase):
    enemy = Enemy()
    enemy.health += health_increase # increase the health of the enemy
    enemy.speedy += speed_increase  # Increase the speed based on difficulty
    return enemy


# Main game loop
def main_game_loop():
    global score
    score = 0  # Initialize the score
    global player_name 
    player_name = get_player_name(screen)  # Get player name before starting

    if player_name is None:
        return  # If the player quits while entering name, exit the game

    all_sprites = pygame.sprite.Group()  
    bullets = pygame.sprite.Group()  
    enemies = pygame.sprite.Group() 
    powerups = pygame.sprite.Group()
    speedups = pygame.sprite.Group()

    player = Player(all_sprites, bullets)  # Pass all_sprites and bullets to Player
    all_sprites.add(player)

    # Create initial enemies
    for i in range(8):
        enemy = spawn_enemy(0, 0)  # Initial speed, no increase yet
        all_sprites.add(enemy)
        enemies.add(enemy)

    # Game variables
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)  # Font for displaying score
    difficulty_timer = pygame.time.get_ticks()  # Start the difficulty timer
    powerup_timer = pygame.time.get_ticks() #Start the powerup timer
    speedup_timer = pygame.time.get_ticks() # Start the speedup timer
    speed_increase = 1  # Amount to increase speed each difficulty increment
    health_increase = 1 # Amount to increase health every

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                pass

        all_sprites.update()

        # Pixel-perfect collision detection between player and enemies
        collisions = pygame.sprite.spritecollide(player, enemies, True, pygame.sprite.collide_mask)
        for collision in collisions:
            player.lives -= 1  # Reduce player's lives by 1
            enemy = spawn_enemy(speed_increase, health_increase)  # Spawn a new enemy with increased speed
            all_sprites.add(enemy)
            enemies.add(enemy)
            if player.lives <= 0:
                game_over(screen, player_name)
                running = False

        hits = pygame.sprite.groupcollide(enemies, bullets, False, True)  # False to keep the enemy, True to destroy the bullet
        for hit in hits:
            hit.take_damage(1)  # Reduce health by 1 on bullet hit
            score += 10
            if hit.health <= 0:
                hit.kill()  # Destroy the enemy if health reaches 0
            enemy = spawn_enemy(speed_increase, health_increase)  # Spawn a new enemy with increased speed and health
            all_sprites.add(enemy)
            enemies.add(enemy)
        
        powerup_hits = pygame.sprite.spritecollide(player, powerups, True)
        for powerup in powerup_hits:
            player.increase_bullet_count()  # Increase the number of bullets

        speedup_hits = pygame.sprite.spritecollide(player, speedups, True)
        for speedup in speedup_hits:
            player.increase_speed() 

        # Spawn a new power-up every 13 seconds
        current_time = pygame.time.get_ticks()
        if current_time - powerup_timer > 13000:  # 20 seconds interval
            powerup = PowerUp()
            all_sprites.add(powerup)
            powerups.add(powerup)
            powerup_timer = current_time  # Reset power-up timer
        
        # Spawn a new power-up every 16 seconds
        if current_time - speedup_timer > 16000:  # 20 seconds interval
            speedup = SpeedUp()
            all_sprites.add(speedup)
            speedups.add(speedup)
            speedup_timer = current_time  # Reset speed-up timer

        # increase difficulty
        if current_time - difficulty_timer > 18000:
            speed_increase += 1  # Increase enemy speed
            health_increase += 1
            # Spawn additional enemies as the difficulty increases
            for _ in range(3):  # Spawn 3 additional enemies each time difficulty increases
                enemy = spawn_enemy(speed_increase, health_increase)
                all_sprites.add(enemy)
                enemies.add(enemy)
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

# Start the game
main_game_loop()