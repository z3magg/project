#Sound by Jan125
# Импортируем все нужные библиотеки
import pygame
import random
from os import path
from pygame.locals import *

# Задаём путь к файлам
image_dir = path.join(path.dirname(__file__), 'image')
snd_dir = path.join(path.dirname(__file__), 'sounds')

# Задаём размеры окна и частоту обновления
WIDTH = 1920
HEIGHT = 1080
FPS = 90
POWERUP_TIME = 5000

# Задаем цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)


# Создаем окно для игры
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Survival!") # Задаём название игры
clock = pygame.time.Clock()

font_name = pygame.font.match_font('arial') # Задаём шрифт для текста

# Делаем задний фон анимированный
background = pygame.image.load(path.join(image_dir, 'starfield.png')).convert() # Загружаем картинку заднего фона
background_rect = background.get_rect()
background1 = background.copy()
background2 = background.copy()
background1_y = 0 
background_speed = 4

# Создаём функцию для отрисовки текста
def draw_text(surf, text, size, x, y):
    font = pygame.font.Font(font_name, size)
    text_surface = font.render(text, True, WHITE)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x, y)
    surf.blit(text_surface, text_rect)      

# Создаём функцию для метеоритов
def newmob():
    m = Mob()
    all_sprites.add(m)
    mobs.add(m)

# Функция для отображения здоровья
def draw_shield_bar(surf, x, y, pct):
    if pct < 0:
        pct = 0
    BAR_LENGTH = 300
    BAR_HEIGHT = 15
    fill = (pct / 100) * BAR_LENGTH
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT)
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT)
    pygame.draw.rect(surf, RED, fill_rect)
    pygame.draw.rect(surf, WHITE, outline_rect, 2)

# Функция для отображения жизней
def draw_lives(surf, x, y, lives, img):
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x + 65 * i
        img_rect.y = y
        surf.blit(img, img_rect)

# Функция для начального экрана
def show_go_screen():
    screen.blit(background, background_rect)
    draw_text(screen, "SPACE SURVIVAL", 64, WIDTH / 2, HEIGHT / 4)
    draw_text(screen, "Arrow keys move, Space to fire", 22,
              WIDTH / 2, HEIGHT / 2)
    draw_text(screen, "Press a key to begin", 18, WIDTH / 2, HEIGHT * 3 / 4)
    pygame.display.flip()
    waiting = True
    while waiting:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYUP:
                waiting = False

 
    
# Создаём спрайт игрока
class Player(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(player_img, (100, 100))
        self.image.set_colorkey(WHITE)
        self.rect = self.image.get_rect()
        self.radius = 45 
        self.rect.centerx = WIDTH / 2
        self.rect.bottom = HEIGHT / 1.2
        self.speedx = 0                           
        self.speedy = 0
        self.shield = 100
        self.shoot_delay = 250
        self.last_shot = pygame.time.get_ticks()
        self.lives = 3
        self.hidden = False
        self.hide_timer = pygame.time.get_ticks()
        self.power = 1
        self.power_time = pygame.time.get_ticks()
   
    # Прописываем движение и ограничения по сторонам, чтобы игрок не мог выйти за пределы окна
    
    def update(self):
        # время для бонусов
        if self.power >= 2 and pygame.time.get_ticks() - self.power_time > POWERUP_TIME:
            self.power -= 1
            self.power_time = pygame.time.get_ticks()
        
        # Отображение
        if self.hidden and pygame.time.get_ticks() - self.hide_timer > 0:
            self.hidden = False
            self.rect.centerx = WIDTH / 2
            self.rect.bottom = HEIGHT - 10
        # Прописываем управление и ограничения
        self.speedx = 0
        self.speedy = 0
        keystate = pygame.key.get_pressed()
        if keystate[pygame.K_LEFT]:
            self.speedx = -8
        if keystate[pygame.K_RIGHT]:
            self.speedx = 8
        if keystate[pygame.K_UP]:
            self.speedy = 8
        if keystate[pygame.K_DOWN]:
            self.speedy = -8
        if keystate[pygame.K_SPACE]:
            self.shoot()
        self.rect.x += self.speedx
        self.rect.y -= self.speedy
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > HEIGHT:
            self.rect.bottom = HEIGHT
    # функция для подбора бонуса
    def powerup(self):
        self.power += 1
        self.power_time = pygame.time.get_ticks()
        
    # Создаём функцию выстрелов
    def shoot(self):
        now = pygame.time.get_ticks()
        if now - self.last_shot > self.shoot_delay:
            self.last_shot = now
            if self.power == 1:
                bullet = Bullet(self.rect.centerx, self.rect.top)
                all_sprites.add(bullet)
                bullets.add(bullet)
                shoot_snd.play()
            if self.power >= 2:
                bullet1 = Bullet(self.rect.left, self.rect.centery)
                bullet2 = Bullet(self.rect.right, self.rect.centery)
                all_sprites.add(bullet1)
                all_sprites.add(bullet2)
                bullets.add(bullet1)
                bullets.add(bullet2)
                shoot_snd.play()
    
    def hide(self):
    # временно скрыть игрока
        self.hidden = True
        self.hide_timer = pygame.time.get_ticks()
        self.rect.center = (WIDTH / 2, HEIGHT + 200)
        
# Делаем анимацию для взрыва
class Explosion(pygame.sprite.Sprite):
    
    def __init__(self, center, size):
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = explosion_anim[self.size][0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 60
        
    # Делаем функцию для взрыва
    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(explosion_anim[self.size]):
                self.kill()
            else:
                center = self.rect.center
                self.image = explosion_anim[self.size][self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center                

# Создаём спрайт метеорита
class Mob(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image_orig = random.choice(meteor_images)
        self.image_orig.set_colorkey(BLACK)
        self.image = self.image_orig.copy()
        self.rect = self.image.get_rect()
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width * .85 / 2)
        #pygame.draw.circle(self.image, RED, self.rect.center, self.radius)
        self.rect.x = random.randrange(WIDTH - self.rect.width)
        self.rect.y = random.randrange(-100, -40)
        self.speedy = random.randrange(1, 40)
        self.speedx = random.randrange(-3, 20)
        self.rot = 0
        self.rot_speed = random.randrange(-8, 8)
        self.last_update = pygame.time.get_ticks()
        
    # Создаём функцию, чтобы метеорит крутился 
    def rotate(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > 50:
            self.last_update = now
            self.rot = (self.rot + self.rot_speed) % 360
            new_image = pygame.transform.rotate(self.image_orig, self.rot)
            old_center = self.rect.center
            self.image = new_image
            self.rect = self.image.get_rect()
            self.rect.center = old_center
			
    # вращение спрайтов

    def update(self):
        self.rotate()
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        if self.rect.top > HEIGHT + 10 or self.rect.left < -25 or self.rect.right > WIDTH + 20:
            self.rect.x = random.randrange(WIDTH - self.rect.width)
            self.rect.y = random.randrange(-100, -40)
            self.speedy = random.randrange(1, 8)

# Создаём спрайт выстрелов
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.image = lazer_img
        self.rect = self.image.get_rect()
        self.rect.bottom = y
        self.rect.centerx = x
        self.speedy = -10
    # Задаём движение для выстрела
    def update(self):
        self.rect.y += self.speedy
        # убить, если он заходит за верхнюю часть экрана
        if self.rect.bottom < 0:
            self.kill()
# Создаём спрайт для бонусов 
class Pow(pygame.sprite.Sprite):
    def __init__(self, center):
        pygame.sprite.Sprite.__init__(self)
        self.type = random.choice(['shield', 'gun'])
        self.image = powerup_images[self.type]
        self.image.set_colorkey(WHITE)
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speedy = 6
    # Задаём движение для бонуса
    def update(self):
        self.rect.y += self.speedy
        # убить, если он сдвинется с нижней части экрана
        if self.rect.top > HEIGHT:
            self.kill()


# Вся графика игры
player_img = pygame.image.load(path.join(image_dir, "starship.png")).convert()
player_mini_img = pygame.transform.scale(player_img, (60, 60))
player_mini_img.set_colorkey(WHITE)
lazer_img = pygame.image.load(path.join(image_dir, 'laser.png')).convert()
meteor_images = []
meteor_list = ['meteorGrey_big1.png', 'meteorGrey_big2.png', 'meteorGrey_big3.png',
               'meteorGrey_big4.png', 'meteorGrey_med1.png', 'meteorGrey_med2.png',
               'meteorGrey_small1.png', 'meteorGrey_small2.png', 'meteorGrey_tiny1.png']
for img in meteor_list:
    meteor_images.append(pygame.image.load(path.join(image_dir, img)).convert())
powerup_images = {}
powerup_images['shield'] = pygame.image.load(path.join(image_dir, 'shield.png')).convert()
powerup_images['gun'] = pygame.image.load(path.join(image_dir, 'bolt.png')).convert()

explosion_anim = {}
explosion_anim['lg'] = []
explosion_anim['sm'] = []
explosion_anim['player'] = []
for i in range(9):
    filename = 'regularExplosion0{}.png'.format(i)
    img = pygame.image.load(path.join(image_dir, filename)).convert()
    img.set_colorkey(BLACK)
    img_lg = pygame.transform.scale(img, (75, 75))
    explosion_anim['lg'].append(img_lg)
    img_sm = pygame.transform.scale(img, (32, 32))
    explosion_anim['sm'].append(img_sm)
    filename = 'sonicExplosion0{}.png'.format(i)
    img = pygame.image.load(path.join(image_dir, filename)).convert()
    img.set_colorkey(BLACK)
    explosion_anim['player'].append(img)
    
# Все звуковые эффекты и музыка
shield_sound = pygame.mixer.Sound(path.join(snd_dir, 'bonus_2.wav'))
power_sound = pygame.mixer.Sound(path.join(snd_dir, 'bonus_1.wav'))
shoot_snd = pygame.mixer.Sound(path.join(snd_dir, 'Pew.wav'))
expl_player_snd = pygame.mixer.Sound(path.join(snd_dir, 'Explosion_pl.wav'))
expl_sounds = []
for snd in ['Expl1.wav', 'Expl2.wav']:
    expl_sounds.append(pygame.mixer.Sound(path.join(snd_dir, snd)))
    pygame.mixer.music.load(path.join(snd_dir, 'music.wav'))
    pygame.mixer.music.set_volume(0.3) 
    pygame.mixer.music.play(loops=-1)
    
# Все спрайты
all_sprites = pygame.sprite.Group()
powerups = pygame.sprite.Group()
mobs = pygame.sprite.Group()
bullets = pygame.sprite.Group()
player = Player()
all_sprites.add(player)
for i in range(16):
    newmob()
score = 0


# Цикл игры
game_over = True
running = True
while running:
    if game_over:
        show_go_screen()
        game_over = False
        all_sprites = pygame.sprite.Group()
        mobs = pygame.sprite.Group()
        bullets = pygame.sprite.Group()
        powerups = pygame.sprite.Group()
        player = Player()
        all_sprites.add(player)
        for i in range(12):
            newmob()
        score = 0
        
    # Держим цикл на правильной скорости
    clock.tick(FPS)
    # Ввод процесса (события)
    for event in pygame.event.get():
        # проверка для закрытия окна
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                running = False
    background1_y += background_speed
    if background1_y >= HEIGHT:
        background1_y = 0        
    
    # Обновление
    all_sprites.update()    
       
    # проверка попадания пули в моба
    hits = pygame.sprite.groupcollide(mobs, bullets, True, True)
    for hit in hits:
        score += 50 - hit.radius
        random.choice(expl_sounds).play()
        expl = Explosion(hit.rect.center, 'lg')
        all_sprites.add(expl)
        if random.random() > 0.9:
            pow = Pow(hit.rect.center)
            all_sprites.add(pow)        
            powerups.add(pow)
        newmob()
    

    #Проверка, не ударил ли моб игрока
    hits = pygame.sprite.spritecollide(player, mobs, True, pygame.sprite.collide_circle)
    for hit in hits:
        player.shield -= hit.radius * 2
        expl = Explosion(hit.rect.center, 'sm')
        expl_player_snd.play()
        all_sprites.add(expl)
        newmob()
        if player.shield <= 0:
            death_explosion = Explosion(player.rect.center, 'player')
            all_sprites.add(death_explosion)
            player.hide()
            player.lives -= 1
            player.shield = 100
            
    # Проверка столкновения игрока с улучшением       
    hits = pygame.sprite.spritecollide(player, powerups, True)
    for hit in hits:
        if hit.type == 'shield':
            shield_sound.play()
            player.shield += random.randrange(10, 30)
            if player.shield >= 100:
                player.shield = 100
        if hit.type == 'gun':
            player.powerup()
            power_sound.play()
      
    # Если игрок умер, игра окончена
    if player.lives == 0 and not death_explosion.alive():
        game_over = True
  
    # Рендеринг
    screen.fill(BLACK)
    screen.blit(background, background_rect)
    screen.blit(background1, (0, background1_y - HEIGHT))
    screen.blit(background2, (0, background1_y))
    all_sprites.draw(screen)
    draw_text(screen, str(score), 30, WIDTH / 2, 10)
    draw_shield_bar(screen, 5, 5, player.shield)
    draw_lives(screen, WIDTH - 200, 5, player.lives,
               player_mini_img)
    # После отрисовки всего, переворачиваем экран
    pygame.display.flip()


pygame.quit() 