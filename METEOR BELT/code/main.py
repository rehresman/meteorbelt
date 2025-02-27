import pygame
import random
import math
import os

class Player(pygame.sprite.Sprite):
    def __init__(self, groups):
        super().__init__(groups)
        self.image = pygame.image.load(os.path.join(BASE_DIR, 'images', 'paper spaceship.png')).convert_alpha()
        self.rect = self.image.get_frect(center = (WINDOW_WIDTH/2, WINDOW_HEIGHT/2))
        self.direction = pygame.math.Vector2()
        self.speed = 300

        # cooldown
        self.can_shoot = True
        self.laser_shoot_time = 0
        self.cooldown_duration = 100

        # mask

    def laser_timer(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.laser_shoot_time >= self.cooldown_duration:
                self.can_shoot = True

    def update(self,dt):
        keys = pygame.key.get_pressed()
        self.direction.x = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])
        self.direction.y = int(keys[pygame.K_DOWN]) - int(keys[pygame.K_UP])
        self.direction = self.direction.normalize() if self.direction.length() > 0 else self.direction
        self.rect.center += self.direction * self.speed * dt
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > WINDOW_WIDTH:
            self.rect.right = WINDOW_WIDTH
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > WINDOW_HEIGHT:
            self.rect.bottom = WINDOW_HEIGHT
        recent_keys = pygame.key.get_just_pressed()
        if recent_keys[pygame.K_SPACE] and self.can_shoot:
            Laser(laser_surf, (self.rect.centerx + 5,self.rect.top), all_sprites)
            self.can_shoot = False
            self.laser_shoot_time = pygame.time.get_ticks()
        
        self.laser_timer()

class Star(pygame.sprite.Sprite):
    def __init__(self, groups, surf):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(center = (random.randint(0,WINDOW_WIDTH), random.randint(0,WINDOW_HEIGHT)))

class Laser(pygame.sprite.Sprite):
    def __init__(self, surf, pos, groups):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(midbottom = pos)
        laser_sound.play()

    def update(self, dt):
        self.rect.y -= 400 * dt
        collision = pygame.sprite.spritecollide(self, meteor_sprites, True, pygame.sprite.collide_mask)
        if collision:
            AnimatedExplosion(explosion_frames, self.rect.center, all_sprites)

        if self.rect.bottom < 0 or collision:
            self.kill()

class Meteor(pygame.sprite.Sprite):
    def __init__(self, surf, difficulty, groups):
        super().__init__(groups)
        if random.randint(1,100 - math.floor(101 - difficulty)) > 20:
            self.kill()
        self.image_init = surf
        self.image = self.image_init
        self.rect = self.image.get_frect(center = (random.randint(0,WINDOW_WIDTH), random.randint(-WINDOW_HEIGHT,0)))
        self.direction = pygame.math.Vector2(random.randint(-100,100), random.randint(1,100)).normalize()
        self.speed = random.randint(100, 400)
        self.rotation_speed = random.randint(-80,80)
        self.rotation = 0
        

    def update(self, dt):
        self.rotation += self.rotation_speed * dt
        self.image = pygame.transform.rotozoom(self.image_init, self.rotation, 1)
        self.rect = self.image.get_frect(center = self.rect.center)
        self.rect.y += self.speed * self.direction.y * dt
        self.rect.x += self.speed * self.direction.x * dt
        if self.rect.top > WINDOW_HEIGHT or self.rect.left > WINDOW_WIDTH or self.rect.right < 0:
            self.kill()

class AnimatedExplosion(pygame.sprite.Sprite):
    def __init__(self, frames, pos, groups):
        super().__init__(groups)
        self.image = frames[0]
        self.rect = self.image.get_frect(center = pos)
        self.frames = frames
        self.frame_index = 0
        explosion_sound.play()

    def update(self, dt):
        self.frame_index += 20 * dt
        self.image = self.frames[int(self.frame_index) % len(self.frames)]
        if self.frame_index >= len(self.frames):
            self.kill()


def display_score():
    remaining_distance = DISTANCE - pygame.time.get_ticks()
    if remaining_distance > 0:
        text_surf = font.render('-' + str(remaining_distance) + ' m', True, (240,240,240))
        text_rect = text_surf.get_frect(midtop = (WINDOW_WIDTH/2, 50))
        pygame.draw.rect(display_surface, (240,240,240), text_rect.inflate(20,20).move(0,-9), 5)
    else:
        text_surf = font.render('WINNER!!! YOU SURVIVED!', True, (240,240,240))
        text_rect = text_surf.get_frect(center = (WINDOW_WIDTH/2, WINDOW_HEIGHT/2))
    display_surface.blit(text_surf, text_rect)
    

# general setup
pygame.init()
pygame.mixer.init()
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
NUMBER_OF_STARS = 20
DISTANCE = 211000
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Space Shooter')
running = True
clock = pygame.time.Clock()

# sprite groups
all_sprites = pygame.sprite.Group()
meteor_sprites = pygame.sprite.Group()


# imports


star_surf = pygame.image.load(os.path.join(BASE_DIR, 'images', 'paper star.png')).convert_alpha()
for i in range(NUMBER_OF_STARS):
    Star(all_sprites, star_surf)
player = Player(all_sprites)
meteor_surf = pygame.image.load(os.path.join(BASE_DIR, 'images', 'paper asteroid.png')).convert_alpha()
laser_surf = pygame.image.load(os.path.join(BASE_DIR, 'images', 'laser.png')).convert_alpha()
font = pygame.font.Font(os.path.join(BASE_DIR, 'images', 'Oxanium-Bold.ttf'), 50)
explosion_frames = [pygame.image.load(os.path.join(BASE_DIR, 'images', 'explosion', f'{i}.png')).convert_alpha() for i in range(21)]
laser_sound = pygame.mixer.Sound(os.path.join(BASE_DIR, 'audio', 'laser.wav'))
laser_sound.set_volume(0.3)
explosion_sound = pygame.mixer.Sound(os.path.join(BASE_DIR, 'audio', 'explosion.wav'))
explosion_sound.set_volume(0.6)
game_music = pygame.mixer.Sound(os.path.join(BASE_DIR, 'audio', 'The Forbidden Zone.wav'))
game_music.set_volume(0.8)
game_music.play(0)
background = pygame.image.load(os.path.join(BASE_DIR, 'images', 'bg.png'))
background = pygame.transform.scale(background, (WINDOW_WIDTH + 100,WINDOW_HEIGHT + 100)) 
bg_y = -50
bg_speed = 1                     
difficulty = 1



# custom events -> meteor spawn
meteor_event = pygame.event.custom_type()
pygame.time.set_timer(meteor_event, 100)



while running:
    dt = clock.tick() / 500
    difficulty += dt / 50 
    bg_y = (bg_y + bg_speed) % WINDOW_HEIGHT
    # event loop
    for event in pygame.event.get(): 
        if event.type == pygame.QUIT:
            running = False
        if event.type == meteor_event and DISTANCE - pygame.time.get_ticks() > 0:
            Meteor(meteor_surf, difficulty, (all_sprites, meteor_sprites))

    all_sprites.update(dt)

    # draw the game
    display_surface.blit(background, (0,bg_y))
    display_surface.blit(background, (0,bg_y - WINDOW_HEIGHT))
    display_score()
    all_sprites.draw(display_surface)

    # test collision
    collision_sprites = pygame.sprite.spritecollide(player, meteor_sprites, True, pygame.sprite.collide_mask)
    if collision_sprites:
        pass
        running = False
    pygame.display.update()
pygame.quit()