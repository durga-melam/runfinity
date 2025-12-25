import pygame
import random
import os

pygame.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 800, 240
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Runfinity - Final")

LIGHT_BACKGROUND = (255, 255, 255)
LIGHT_FOREGROUND = (0, 0, 0)

def get_colors():
    return (LIGHT_BACKGROUND, LIGHT_FOREGROUND)

GAME_SPEED = 5
JUMP_VELOCITY = 14
GRAVITY = 1
GROUND_Y = SCREEN_HEIGHT - 30
ANIMATION_SPEED = 5
CLOUD_SPEED = 1

FOX_SIZE = (48, 48)
OBSTACLE_CACTUS_SIZE = (32, 48)
OBSTACLE_ROCK_SIZE = (40, 24)
CLOUD_SIZE = (64, 32)

def load_and_scale_image(name, size):
    path = os.path.join('assets', name)
    image = pygame.image.load(path).convert_alpha()
    return pygame.transform.scale(image, size)

FOX_RUN_IMAGES = [
    load_and_scale_image('fox_run_1.png', FOX_SIZE),
    load_and_scale_image('fox_run_2.png', FOX_SIZE)
]
FOX_IMAGE_JUMP = load_and_scale_image('fox_jump.png', FOX_SIZE)
FOX_IMAGE_HIT = load_and_scale_image('fox_hit.png', FOX_SIZE)

OBSTACLE_IMAGES = [
    load_and_scale_image('obstacle_cactus.png', OBSTACLE_CACTUS_SIZE),
    load_and_scale_image('obstacle_rock.png', OBSTACLE_ROCK_SIZE)
]

CLOUD_IMAGE = load_and_scale_image('cloud.png', CLOUD_SIZE)

class Cloud(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = CLOUD_IMAGE
        self.rect = self.image.get_rect(topleft=(SCREEN_WIDTH, random.randint(10, SCREEN_HEIGHT // 2)))

    def update(self):
        self.rect.x -= CLOUD_SPEED
        if self.rect.right < 0:
            self.kill()

class Fox(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.run_frames = FOX_RUN_IMAGES
        self.frame_index = 0
        self.animation_counter = 0
        self.image = self.run_frames[self.frame_index]
        self.rect = self.image.get_rect(midbottom=(50, GROUND_Y))
        self.is_jumping = False
        self.v_y = 0

    def update(self):
        self.rect.y += self.v_y
        if self.is_jumping:
            self.v_y += GRAVITY
            self.image = FOX_IMAGE_JUMP
        else:
            self.animation_counter += 1
            if self.animation_counter >= ANIMATION_SPEED:
                self.frame_index = (self.frame_index + 1) % len(self.run_frames)
                self.image = self.run_frames[self.frame_index]
                self.animation_counter = 0
        if self.rect.bottom >= GROUND_Y:
            self.rect.bottom = GROUND_Y
            self.is_jumping = False
            self.v_y = 0

    def jump(self):
        if not self.is_jumping:
            self.is_jumping = True
            self.v_y = -JUMP_VELOCITY

    def hit(self):
        self.image = FOX_IMAGE_HIT

class Obstacle(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = random.choice(OBSTACLE_IMAGES)
        self.rect = self.image.get_rect(midbottom=(SCREEN_WIDTH, GROUND_Y))

    def update(self):
        self.rect.x -= GAME_SPEED
        if self.rect.right < 0:
            self.kill()

def show_start_screen():
    background, foreground = get_colors()
    font = pygame.font.Font(None, 36)
    small_font = pygame.font.Font(None, 20)
    waiting = True
    while waiting:
        SCREEN.fill(background)
        prompt = small_font.render("Press SPACE to Start", True, foreground)
        SCREEN.blit(prompt, prompt.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                waiting = False

def show_lost_overlay(final_score, frozen_frame):
    global high_score
    if final_score > high_score:
        high_score = final_score
    background, foreground = get_colors()
    font = pygame.font.Font(None, 36)
    small_font = pygame.font.Font(None, 20)
    overlay = True
    while overlay:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                overlay = False
        SCREEN.blit(frozen_frame, (0, 0))
        pygame.draw.rect(SCREEN, (0, 0, 0), (0, GROUND_Y, SCREEN_WIDTH, 20))
        SCREEN.blit(font.render("GAME OVER", True, foreground), (SCREEN_WIDTH // 2 - 80, SCREEN_HEIGHT // 3))
        SCREEN.blit(small_font.render("Press SPACE to Retry", True, foreground), (SCREEN_WIDTH // 2 - 90, SCREEN_HEIGHT // 2))
        SCREEN.blit(small_font.render(f"Score: {final_score}", True, foreground), (SCREEN_WIDTH - 150, 10))
        SCREEN.blit(small_font.render(f"High Score: {high_score}", True, foreground), (SCREEN_WIDTH - 150, 30))
        pygame.display.flip()

high_score = 0

def game_loop():
    running = True
    clock = pygame.time.Clock()
    score = 0
    font = pygame.font.Font(None, 24)
    player = Fox()
    all_sprites = pygame.sprite.Group(player)
    obstacle_group = pygame.sprite.Group()
    cloud_group = pygame.sprite.Group()
    OBSTACLE_EVENT = pygame.USEREVENT + 1
    CLOUD_EVENT = pygame.USEREVENT + 2
    pygame.time.set_timer(OBSTACLE_EVENT, random.randint(1200, 2500))
    pygame.time.set_timer(CLOUD_EVENT, 3000)

    while running:
        background, foreground = get_colors()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                player.jump()
            if event.type == OBSTACLE_EVENT:
                obstacle = Obstacle()
                all_sprites.add(obstacle)
                obstacle_group.add(obstacle)
                pygame.time.set_timer(OBSTACLE_EVENT, random.randint(1200, 2500))
            if event.type == CLOUD_EVENT:
                cloud_group.add(Cloud())

        all_sprites.update()
        cloud_group.update()
        score += 1

        if not player.is_jumping and pygame.sprite.spritecollideany(player, obstacle_group):
            player.hit()
            SCREEN.fill(background)
            cloud_group.draw(SCREEN)
            all_sprites.draw(SCREEN)
            pygame.draw.rect(SCREEN, (0, 0, 0), (0, GROUND_Y, SCREEN_WIDTH, 20))
            pygame.display.flip()
            frozen_frame = SCREEN.copy()
            pygame.time.delay(300)
            show_lost_overlay(score // 10, frozen_frame)
            return score // 10

        SCREEN.fill(background)
        cloud_group.draw(SCREEN)
        all_sprites.draw(SCREEN)
        pygame.draw.rect(SCREEN, (0, 0, 0), (0, GROUND_Y, SCREEN_WIDTH, 20))
        SCREEN.blit(font.render(f"Score: {score // 10}", True, foreground), (10, 10))
        pygame.display.flip()
        clock.tick(60)

def main():
    show_start_screen()
    while True:
        game_loop()

if __name__ == "__main__":
    main()
