import pygame
import random
import os

#貞數, 視窗大小
FPS = 60
WIDTH = 500
HEIGHT = 600

#顏色
BLACK = (0,0,0)
WHITE = (255,255,255)
GREEN = (0,255,0)
RED = (255,0,0)
YELLOW = (255,255,0)


# 遊戲初始化 and 創建視窗
pygame.init() #初始化
pygame.mixer.init() #音樂初始化
screen = pygame.display.set_mode((WIDTH,HEIGHT))
pygame.display.set_caption("雷霆戰機") #遊戲(視窗)名稱
clock = pygame.time.Clock()
running = True

#載入圖片
background_img = pygame.image.load(os.path.join("img", "background.png")).convert() #背景圖片
rocket_img = pygame.image.load(os.path.join("img", "rocketship.png")).convert() #火箭圖片
rocket_mini_img = pygame.transform.scale(rocket_img,(25,19)) #圖示剩餘生命
rocket_mini_img.set_colorkey(BLACK)
pygame.display.set_icon(rocket_mini_img)
bullet_img = pygame.image.load(os.path.join("img", "lazerBullet.png")).convert() #子彈圖片
rock_imgs=[] #石頭圖片列表
for i in range(7): #讀取7張圖片
    rock_imgs.append(pygame.image.load(os.path.join("img", f"rock{i}.png")).convert())
expl_anim = {} #爆炸動畫字典
expl_anim['lg'] = [] #大型爆炸列表
expl_anim['sm'] = [] #小型爆炸列表
expl_anim['player'] = [] #火箭爆炸列表
for i in range(9): #讀取九種爆炸動畫
    expl_img = pygame.image.load(os.path.join("img",f"expl{i}.png")).convert()
    expl_img.set_colorkey(BLACK)
    expl_anim['lg'].append(pygame.transform.scale(expl_img,(75,75)))
    expl_anim['sm'].append(pygame.transform.scale(expl_img,(30,30)))

    player_expl_img = pygame.image.load(os.path.join("img",f"player_expl{i}.png")).convert() #火箭爆炸動畫
    player_expl_img.set_colorkey(BLACK)
    expl_anim['player'].append(player_expl_img)
power_imgs = {}
power_imgs['shield'] = pygame.image.load(os.path.join("img","shield.png")).convert()
power_imgs['gun'] = pygame.image.load(os.path.join("img","gun.png")).convert()


#載入音樂
shoot_sound = pygame.mixer.Sound(os.path.join("sound","shoot.wav")) #射擊音效
shield_sound = pygame.mixer.Sound(os.path.join("sound","pow0.wav")) #獲得護盾音效
gun_sound = pygame.mixer.Sound(os.path.join("sound","pow1.wav")) #獲得閃電音效
Dead_sound = pygame.mixer.Sound(os.path.join("sound","rumble.ogg")) #爆炸死亡音效
expl_sounds = [ #兩種爆炸音效
    pygame.mixer.Sound(os.path.join("sound","expl0.wav")),
    pygame.mixer.Sound(os.path.join("sound","expl1.wav"))
]
pygame.mixer.music.load(os.path.join("sound","background.ogg")) #背景音樂
pygame.mixer.music.set_volume(0.4) #背景音樂音量大小






font_name = os.path.join("font.ttf") #引入通用字體
def draw_text(surf, text, size, x, y): #分數文字內容
    font = pygame.font.Font(font_name, size) #傳入字體與大小
    text_surface =  font.render(text, True, WHITE) #使用
    text_rect = text_surface.get_rect() #文字定位
    text_rect.centerx = x #定位
    text_rect.top = y #定位
    surf.blit(text_surface, text_rect) 

def new_rock(): #函式 :生成石頭
    r = Rock()
    all_sprites.add(r)
    rocks.add(r)

def draw_health(surf, hp, x, y): #函式 :血條
    if hp < 0:
        hp = 0
    BAR_LENGTH = 100 #血條長度
    BAR_HEIGHT = 10  #血條高度
    fill = (hp/100)*BAR_LENGTH #剩多少血
    outline_rect = pygame.Rect(x, y, BAR_LENGTH, BAR_HEIGHT) #血條外框
    fill_rect = pygame.Rect(x, y, fill, BAR_HEIGHT) #填滿外框
    pygame.draw.rect(surf, GREEN,fill_rect) #血條本身顏色
    pygame.draw.rect(surf, WHITE, outline_rect, 2) #血條外框顏色

def draw_lives(surf, lives, img, x, y): #函式 :剩餘生命
    for i in range(lives):
        img_rect = img.get_rect()
        img_rect.x = x +32*i #生命顯示間隔32px
        img_rect.y = y
        surf.blit(img, img_rect)

def draw_init(): #遊戲開始畫面
    screen.blit(background_img, (0,0)) #背景圖顯示
    draw_text(screen,'雷霆戰機機',64, WIDTH/2, HEIGHT/4)
    draw_text(screen,'< > 移動火箭 Space發射子彈',22, WIDTH/2, HEIGHT/2)
    draw_text(screen,'按任意鍵開始遊戲 !',18, WIDTH/2, HEIGHT*3/4)
    pygame.display.update()
    waiting = True
    while waiting :
        clock.tick(FPS)
        #取得輸入
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return True
            elif event.type == pygame.KEYUP:
                waiting = False
                return False


class Player(pygame.sprite.Sprite): #類別 : 玩家、火箭

    def __init__(self): #火箭初始化位置
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.scale(rocket_img,(40,55))
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.radius = 20
        #pygame.draw.circle(self.image,RED,self.rect.center,self.radius)
        self.rect.centerx = WIDTH/2 #火箭生成位置
        self.rect.bottom = HEIGHT - 10 #火箭生成位置
        self.speedx = 8 #火箭移動速度
        self.health = 100
        self.lives = 3
        self.hidden = False
        self.hide_time = 0
        self.gun = 1
        self.gun_time = 0

    def update(self): 
        now = pygame.time.get_ticks()
        if self.gun > 1 and now - self.gun_time > 5000: #子彈升級時間持續5秒
            self.gun -= 1
            self.gun_time = now
        if self.hidden and now - self.hide_time > 1000: #1秒後重生
            self.hidden = False
            self.rect.centerx = WIDTH/2 
            self.rect.bottom = HEIGHT - 10 
        key_pressed = pygame.key.get_pressed() #控制火箭移動
        if key_pressed[pygame.K_RIGHT]:
            self.rect.x += self.speedx
        if key_pressed[pygame.K_LEFT]:
            self.rect.x -= self.speedx 
        if self.rect.right > WIDTH:
            self.rect.right = WIDTH
        if self.rect.left < 0:
            self.rect.left = 0

    def shoot(self): #火箭射擊
        if not(self.hidden):  
            if self.gun == 1: #子彈Lv1
                bullet = Bullet(self.rect.centerx, self.rect.top)
                all_sprites.add(bullet)
                bullets.add(bullet)
                shoot_sound.play()
            elif self.gun >=2: #子彈Lv2
                bullet1 = Bullet(self.rect.left, self.rect.centery)
                bullet2 = Bullet(self.rect.right, self.rect.centery)
                all_sprites.add(bullet1)
                all_sprites.add(bullet2)
                bullets.add(bullet1)
                bullets.add(bullet2)
                shoot_sound.play()

    def hide(self): #火箭死亡
        self.hidden = True
        self.hide_time = pygame.time.get_ticks()
        self.rect.center =  (WIDTH/2, HEIGHT+500)
    def gunup(self): #子彈升級
        self.gun += 1
        self.gun_time = pygame.time.get_ticks()

class Rock(pygame.sprite.Sprite): #類別 : 石頭
    def __init__(self): #石頭初始化位置
        pygame.sprite.Sprite.__init__(self)
        self.image_ori = random.choice(rock_imgs) #隨機生成原圖片
        self.image_ori.set_colorkey(BLACK) #去掉圖片底色
        self.image = self.image_ori.copy() #複製原圖片
        self.rect = self.image.get_rect()
        self.radius = int(self.rect.width * 0.85 /2) #石頭半徑大小,由於分數原因, 需要轉回整數
        #pygame.draw.circle(self.image,RED,self.rect.center,self.radius)
        self.rect.x = random.randrange(0,WIDTH-self.rect.width)
        self.rect.y = random.randrange(-180,-100) #石頭生成位置
        self.speedy = random.randrange(2,10) #石頭下墜
        self.speedx = random.randrange(-3,3) #石頭平移
        self.total_degree = 0 #轉動總角度
        self.rot_degree = random.randrange(-3,3)  #每次轉動角度(隨機)
    
    def rotate(self): #轉動石頭圖片
        self.total_degree += self.rot_degree #轉動角度疊加
        self.total_degree = self.total_degree % 360  #轉超過一圈後對360度取餘數, 回到0度
        self.image = pygame.transform.rotate(self.image_ori, self.total_degree)
        center = self.rect.center #原先定位的中心點
        self.rect = self.image.get_rect() #對轉動後的圖片重新定位
        self.rect.center = center #設定回原中心點

    def update(self): #石頭轉動速度與更新位置
        self.rotate()
        self.rect.y += self.speedy
        self.rect.x += self.speedx
        if self.rect.top > HEIGHT or self.rect.left > WIDTH or self.rect.right < 0:
            self.rect.x = random.randrange(0,WIDTH-self.rect.width)
            self.rect.y = random.randrange(-100,-40)
            self.speedy = random.randrange(2,10)
            self.speedx = random.randrange(-3,3)

class Bullet(pygame.sprite.Sprite): #類別 : 子彈
    def __init__(self, x, y): #子彈初始化位置
        pygame.sprite.Sprite.__init__(self)
        self.image = bullet_img
        self.image.set_colorkey(BLACK)  
        self.rect = self.image.get_rect()
        self.rect.centerx = x
        self.rect.bottom = y
        self.speedy = -10
        

    def update(self): #子彈移動速度與更新位置
        self.rect.y += self.speedy
        if self.rect.bottom < 0:
            self.kill()

class Explosion(pygame.sprite.Sprite): #類別 : 爆炸動畫
    def __init__(self, center, size): #爆炸圖片更新位置
        pygame.sprite.Sprite.__init__(self)
        self.size = size
        self.image = expl_anim[self.size][0]  
        self.rect = self.image.get_rect() #定位
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks() #從初始化到現在經過的毫秒數
        self.frame_rate = 50 #過多久換下一張爆炸圖片
        
    def update(self): #根據經過的時間更新爆炸圖片, 形成動畫
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(expl_anim[self.size]): #完成一個動畫後消失
                self.kill()
            else:
                self.image = expl_anim[self.size][self.frame]
                center = self.rect.center
                self.rect = self.image.get_rect()
                self.rect.center = center

class Power(pygame.sprite.Sprite): #類別 : 寶物
    def __init__(self, center): 
        pygame.sprite.Sprite.__init__(self)
        self.type = random.choice(['shield','gun'])
        self.image = power_imgs[self.type]
        self.image.set_colorkey(BLACK)  
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.speedy = 3 #掉落速度
        

    def update(self): #寶物掉落速度與更新位置
        self.rect.y += self.speedy
        if self.rect.top> HEIGHT:
            self.kill()                     

all_sprites = pygame.sprite.Group()
rocks = pygame.sprite.Group() #石頭群組
bullets = pygame.sprite.Group() #子彈群組
powers = pygame.sprite.Group() #寶物群組
player = Player() #火箭群組
all_sprites.add(player)
for i in range(8):
    new_rock()
score = 0 
pygame.mixer.music.play(-1) #背景音樂重複播放

#遊戲迴圈
show_init = True
running = True
while running :
    if show_init :
        close = draw_init()
        if close:
            break
        show_init = False
        all_sprites = pygame.sprite.Group()
        rocks = pygame.sprite.Group() #石頭群組
        bullets = pygame.sprite.Group() #子彈群組
        powers = pygame.sprite.Group() #寶物群組
        player = Player() #火箭群組
        all_sprites.add(player)
        for i in range(8):
            new_rock()
        score = 0
    clock.tick(FPS)
    #取得輸入
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                player.shoot()

    #更新遊戲
    all_sprites.update()
    #判斷子彈與石頭是否有碰撞,回傳字典,key:rocks, value:bullets
    hits = pygame.sprite.groupcollide(rocks, bullets,True ,True) 
    for hit in hits:
        random.choice(expl_sounds).play() #隨機爆炸聲音
        score += hit.radius #根據碰撞到的石頭之半徑大小給予分數
        expl = Explosion(hit.rect.center, 'lg') #子彈打中石頭的動畫
        all_sprites.add(expl) #加入all_sprites才會顯示
        if random.random() > 0.9: #掉落寶物機率
            pow = Power(hit.rect.center)
            all_sprites.add(pow)
            powers.add(pow)
        new_rock()


    #石頭與火箭相撞後,回傳列表裡所有石頭 
    hits = pygame.sprite.spritecollide(player,rocks, True, pygame.sprite.collide_circle) #本體判斷為圓形
    for hit in hits:
        new_rock()
        player.health -= hit.radius #根據石頭半徑大小扣血
        expl = Explosion(hit.rect.center, 'sm') #石頭打中火箭的動畫
        all_sprites.add(expl) #加入all_sprites才會顯示
        if player.health <= 0:
            Dead = Explosion(player.rect.center, 'player')
            all_sprites.add(Dead)
            Dead_sound.play() #死亡音效播放
            player.lives -= 1
            player.health = 100
            player.hide()

    #判斷寶物跟火箭相撞       
    hits = pygame.sprite.spritecollide(player,powers, True)
    for hit in hits :
        if hit.type == 'shield':
            player.health += 20
            if player.health > 100:
                player.health = 100
            shield_sound.play() #護盾音效播放
        elif hit.type == 'gun':
            player.gunup()
            gun_sound.play() #獲得閃電音效播放
    if player.lives == 0 and not (Dead.alive()): #生命歸零時遊戲結束
        show_init = True

    #畫面顯示
    screen.blit(background_img, (0,0)) #背景圖定位在原點
    all_sprites.draw(screen)
    draw_text(screen, str(score), 18, WIDTH/2, 10) #分數顯示 中間,top
    draw_health(screen, player.health, 5, 15) #血條顯示
    draw_lives(screen, player.lives, rocket_mini_img, WIDTH -100, 15) #剩餘生命顯示
    pygame.display.update()

pygame.quit()

