import pygame
from os.path import join
import random

class Player(pygame.sprite.Sprite):
    def __init__(self,groups):
        super().__init__(groups)
        self.image = pygame.image.load(join('images','player.png')).convert_alpha()
        self.rect = self.image.get_rect(center = (WINDOW_WIDTH //2,WINDOW_HEIGHT//2))
        self.player_direction = pygame.math.Vector2()
        self.player_speed = 300

        #cooldown period
        self.can_shoot = True
        self.laser_shoot_time = 0
        self.cooldown_duration = 800
        self.laser_energy = 10

        self.mask =  pygame.mask.from_surface(self.image)

    def laser_timer(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.laser_shoot_time >= self.cooldown_duration:
                self.can_shoot = True

    def update(self ,dt):
        self.keys = pygame.key.get_pressed()
        self.player_direction.x = int(self.keys[pygame.K_RIGHT]) -int(self.keys[pygame.K_LEFT])
        self.player_direction.y = int(self.keys[pygame.K_DOWN]) -int(self.keys[pygame.K_UP])
        self.player_direction = self.player_direction.normalize() if self.player_direction else self.player_direction
        self.rect.center += self.player_direction * self.player_speed * dt

        if self.keys[pygame.K_SPACE] and self.can_shoot and self.laser_energy > 0:
            Laser(laser_surf,self.rect.midtop,(all_sprites, laser_sprites))
            self.can_shoot = False
            self.laser_shoot_time = pygame.time.get_ticks()
            self.laser_energy -= 1
            laser_sound.play()

        self.laser_timer()

class Star(pygame.sprite.Sprite):
    def __init__(self,groups,surf):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_rect(center = (random.randint(20, WINDOW_WIDTH- 10),random.randint(20, WINDOW_HEIGHT- 10)))

class Laser(pygame.sprite.Sprite):
    def __init__(self, laser_surf, pos, groups):
        super().__init__(groups)
        self.image = laser_surf
        self.rect = self.image.get_rect(midbottom = pos)

    def update (self,dt):
        self.rect.centery -= 400 * dt
        if self.rect.bottom < 0:
            self.kill()

class Meteor(pygame.sprite.Sprite):
    def __init__(self,surf, pos, groups):
        super().__init__(groups)
        self.original_image = surf
        self.image = self.original_image
        self.rect = self.image.get_rect(center = pos)
        self.start_time = pygame.time.get_ticks()
        self.lifetime = 3000
        self.direction = pygame.Vector2(random.uniform(-0.5,0.5),1)
        self.speed = random.randint(400,500)
        self.rotation_speed = random.randint(40,80)
        self.rotation = 0

    def update(self,dt):
        self.rect.center += self.direction * self.speed * dt

        if pygame.time.get_ticks() - self.start_time >= self.lifetime:
            self.kill()

        self.rotation += self.rotation_speed * dt
        self.image = pygame.transform.rotozoom(self.original_image, self.rotation, 1)
        self.rect = self.image.get_rect(center = self.rect.center)

class Bullet(pygame.sprite.Sprite):
        def __init__(self, surf, pos, groups):
            super().__init__(groups)
            self.image = surf
            self.rect = self.image.get_rect(center=pos)
            self.start_time = pygame.time.get_ticks()
            self.lifetime = 4000

        def update(self):
            if pygame.time.get_ticks() - self.start_time >= self.lifetime:
                self.kill()

class AnimatedExplosion(pygame.sprite.Sprite):
    def __init__(self, frames, pos, groups):
        super().__init__(groups)
        self.frame = frames
        self.frame_index = 0
        self.image = self.frame[self.frame_index]
        self.rect = self.image.get_rect(center = pos)
        self.frame = explosion_frames

    def update(self,dt):
        self.frame_index += 20 * dt
        if self.frame_index < len(self.frame):
             self.image = self.frame[int(self.frame_index) % len(self.frame)]
        else:
            self.kill


def collisions(player):
    global running
    global score
    collision_sprites = pygame.sprite.spritecollide(player, meteor_sprites, True, pygame.sprite.collide_mask)
    if collision_sprites:
        running = False

    for laser in laser_sprites:
        collided_sprites = pygame.sprite.spritecollide(laser, meteor_sprites, True)
        if collided_sprites:
            laser.kill()
            AnimatedExplosion(explosion_frames,laser.rect.midtop, all_sprites)
            explosion_sound.play()
            score += 1
    pygame.display.set_caption(f'your score: {score} laser energy {player.laser_energy}')

    bullet_collision = pygame.sprite.spritecollide(player,bullet_sprites,True)
    if bullet_collision:
        player.laser_energy += 5

def display_score():
    current_time = pygame.time.get_ticks() //100
    text_surf = font.render(str(current_time), True, (250, 235, 240))
    text_rect = text_surf.get_rect(midbottom = (WINDOW_WIDTH//2,WINDOW_HEIGHT - 50))
    display_surface.blit(text_surf, text_rect)
    pygame.draw.rect(display_surface,(250,235,240),text_rect.inflate(20,30).move(0,-5),5,10)

#general setup
pygame.init()
WINDOW_WIDTH, WINDOW_HEIGHT = 1280,720
display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
running = True
clock = pygame.time.Clock()
score = 0
laser_energy = 10

#import section
star_surf = pygame.image.load(join('images', 'star.png')).convert_alpha()
meteor_surf = pygame.image.load(join('images','meteor.png')).convert_alpha()
laser_surf = pygame.image.load(join('images','laser.png')).convert_alpha()
font = pygame.font.Font(join('images','Oxanium-Bold.ttf'), 40)
explosion_frames = [pygame.image.load(join('images','explosion',f'{i}.png')).convert_alpha() for i in range(21)]
laser_sound = pygame.mixer.Sound(join('audio','laser.wav'))
laser_sound.set_volume(0.1)
explosion_sound = pygame.mixer.Sound(join('audio','explosion.wav'))
game_music = pygame.mixer.Sound(join('audio','game_music.wav'))
game_music.set_volume(0.1)
game_music.play(loops = -1)
bullet_surf = pygame.image.load(join('images','bullet.png')).convert_alpha()

all_sprites = pygame.sprite.Group()
meteor_sprites = pygame.sprite.Group()
laser_sprites = pygame.sprite.Group()
bullet_sprites = pygame.sprite.Group()

for i in range(20):
    Star(all_sprites,star_surf)

player = Player(all_sprites)

#custom events
meteor_event = pygame.event.custom_type()
pygame.time.set_timer(meteor_event, 500)

bullet_event = pygame.event.custom_type()
pygame.time.set_timer(bullet_event, 10000)

while running:
    dt = clock.tick() / 1000

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == meteor_event:
            x, y = random.randint(0, WINDOW_WIDTH), random.randint(-200,-100)
            Meteor(meteor_surf, (x, y), (all_sprites,meteor_sprites))
        if event.type == bullet_event:
            x,y = random.randint(0, WINDOW_WIDTH -5), random.randint(0,WINDOW_HEIGHT -20)
            Bullet(bullet_surf,(x,y),(bullet_sprites))

    all_sprites.update(dt)
    bullet_sprites.update()
    collisions(player)

    display_surface.fill('grey')
    display_score()
    all_sprites.draw(display_surface)
    bullet_sprites.draw(display_surface)

    pygame.display.update()

pygame.quit()