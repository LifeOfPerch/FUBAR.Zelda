import pygame
from settings import *
from support import import_folder

class Player(pygame.sprite.Sprite):
    def __init__(self,pos,groups,obstacle_sprites,create_attack,destroy_attack):
        super().__init__(groups)
        self.image = pygame.image.load("./graphics/test/player.png").convert_alpha()
        self.rect = self.image.get_rect(topleft = pos)
        self.hitbox = self.rect.inflate(0, -26)

        # graphics setup
        self.import_player_assets()
        self.status = 'down'
        self.frame_index = 0
        self.animation_speed = 0.15

        # movement
        self.direction = pygame.math.Vector2()
        self.speed = 10
        self.obstacle_sprites = obstacle_sprites

        # attacking
        self.attacking = False
        self.attack_cd = 1000
        self.attack_time = None

        # weapon
        self.create_attack = create_attack
        self.destroy_attack = destroy_attack
        self.weapon_index = 0
        self.weapon = list(weapon_data.keys())[self.weapon_index]


# loob iga mudeli kasutaja liikumiseks
    def import_player_assets(self):
        character_path = './graphics/player/'
        self.animations =  {'up': [],'down': [],'left': [],'right': [],
			'right_idle':[],'left_idle':[],'up_idle':[],'down_idle':[],
			'right_attack':[],'left_attack':[],'up_attack':[],'down_attack':[]}

        for animation in self.animations.keys():
            full_path = character_path + animation
            self.animations[animation] = import_folder(full_path)

# loob liikumised kasutaja jaoks
    def input(self):
        if not self.attacking:
            keys = pygame.key.get_pressed()

            # movement inputs
            if keys[pygame.K_UP]:
                self.direction.y = -1
                self.status = 'up'
            elif keys[pygame.K_DOWN]:
                self.direction.y = 1
                self.status = 'down'
            else:
                self.direction.y = 0

            if keys[pygame.K_LEFT]:
                self.direction.x = -1
                self.status = 'left'
            elif keys[pygame.K_RIGHT]:
                self.direction.x = 1
                self.status = 'right'
            else:
                self.direction.x = 0

            # attack inputs
            if keys[pygame.K_SPACE]:
                self.attacking = True
                self.attack_time = pygame.time.get_ticks()
                self.create_attack()

            # magic input
            if keys[pygame.K_LCTRL]:
                self.attacking = True
                self.attack_time = pygame.time.get_ticks()

# kontrollib, millega kasutaja tegeleb
    def get_status(self):

        # idle status
        if self.direction.x == 0 and self.direction.y == 0:
            if not 'idle' in self.status and not 'attack' in self.status:
                self.status = self.status + '_idle'
            if not 'idle' in self.status and not 'attack' in self.status:
                self.status = self.status + '_idle'

        if self.attacking:
            self.direction.x = 0
            self.direction.y = 0
            if not 'attack' in self.status:
                if 'idle' in self.status:
                    #overwrite idle
                    self.status = self.status.replace('_idle','_attack')
                else:
                    self.status = self.status + '_attack'
        else:
            if 'attack' in self.status:
                self.status = self.status.replace('_attack', '')

# paneb paika liikumise ja selle kiiruse
    def move(self, speed):
        # Diagonaalse liikumise kiiruse normaliseerimine
        if self.direction.magnitude() != 0:
            self.direction = self.direction.normalize()

        self.hitbox.x += self.direction.x * speed
        self.collision('horizontal')
        self.hitbox.y += self.direction.y * speed
        self.collision('vertical')
        self.rect.center = self.hitbox.center


        # speed instead of self.speed because enemies will inherit same class!
        #self.rect.center += self.direction * speed

# vaatab, kas kasutaja p6rkub millegagi kokku
    def collision(self, direction):
        if direction == "horizontal":
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.x > 0: # moving right
                        self.hitbox.right = sprite.hitbox.left
                    if self.direction.x < 0: # moving left
                        self.hitbox.left = sprite.hitbox.right

        if direction == "vertical":
            for sprite in self.obstacle_sprites:
                if sprite.hitbox.colliderect(self.hitbox):
                    if self.direction.y > 0: # moving down
                        self.hitbox.bottom = sprite.hitbox.top
                    if self.direction.y < 0: # moving up
                        self.hitbox.top = sprite.hitbox.bottom

#kontrollib kas kasutaja saab uuesti runnata
    # kustutab vana relva, timer sobib ideaalselt
    def CD(self):
        current_time = pygame.time.get_ticks()

        if self.attacking:
            if current_time - self.attack_time >= self.attack_cd:
                self.attacking = False
                self.destroy_attack()


# k4ib l4bi k6ik animatsioonid ja alustab tsuklit algusest
    # vaatab, et animatsiooni asuks samas kohas(paneb keskkohad samasse punkti)
    def animate(self):
        animation = self.animations[self.status]

        # loop over the frame index
        self.frame_index += self.animation_speed
        if self.frame_index >= len(animation):
            self.frame_index = 0

        # set the image
        self.image = animation[int(self.frame_index)]
        self.rect = self.image.get_rect(center = self.hitbox.center)

# kontrollib k6iki funktsioone
    def update(self):
        self.input()
        self.CD()
        self.get_status()
        self.animate()
        self.move(self.speed)
