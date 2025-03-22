import pygame
import app  # Contains global settings like WIDTH, HEIGHT, PLAYER_SPEED, etc.
#from bullet import Bullet
import math
from bullet import Bullet

class Player:
    def __init__(self, x, y, assets):
        """Initialize the player with position and image assets."""
        # TODO: 1. Store the player's position
        self.x = x
        self.y = y
        #keep track of velocity for rebound
        self.vx=0
        self.vy=0
        # TODO: 2. Load the player's image from assets

        self.speed = app.PLAYER_SPEED
        self.animations = assets["player"]
        self.beam = assets["beam"][0]
        self.beam_display = [0,0,0,0,False]

        self.state = "idle"
        self.frame_index = 0
        self.animation_timer = 0
        self.animation_speed = 8
        self.xp=0

        # TODO: 3. Create a collision rectangle (self.rect) 
        self.image = self.animations[self.state][self.frame_index]
        self.rect = self.image.get_rect(center=(self.x, self.y))
        self.facing_left=False

        # TODO: 4. Add player health 
        self.health = 5
        self.bullet_speed = 10
        self.bullet_size = 10
        self.bullet_count = 1
        self.shoot_cooldown = 20
        self.shoot_timer = 0
        self.bullets = []#maintains a list of current bullets

    def add_xp(self, amount):
        self.xp += amount

    def handle_input(self):
        """Check and respond to keyboard/mouse input."""
        
        # TODO: 1. Capture Keyboard Input
        # velocity in X, Y direction
        keys = pygame.key.get_pressed()
        resis = 1
        vel_x, vel_y = 0, 0
        # TODO: 2. Adjust player position with keys pressed, updating the player position to vel_x and vel_y
        if keys[pygame.K_LEFT]:
            vel_x-=self.speed+resis
        if keys[pygame.K_RIGHT]:
            vel_x+=self.speed-resis
        if keys[pygame.K_DOWN]:
            vel_y+=self.speed-resis
        if keys[pygame.K_UP]:
            vel_y-=self.speed+resis
        # TODO: 3. Clamp player position to screen bounds

        self.x += vel_x
        self.y+=vel_y
        self.x = max(0,min(self.x,app.WIDTH))
        self.y = max(0,min(self.y,app.HEIGHT))
        self.rect.center = (self.x,self.y)

        #very interesting way of clamping boundaries: usable in info

        #acceleration = velocity/time, this basically already does what you want
        #add friction if u want

        if vel_x != 0 or vel_y != 0:
            self.state = "run"
        else:
            self.state = "idle"

        if vel_x < 0:
            self.facing_left = True
        elif vel_x > 0:
            self.facing_left = False
        pass

    def update(self):
        for bullet in self.bullets:
            bullet.update()
            if bullet.y < 0 or bullet.y > app.HEIGHT or bullet.x < 0 or bullet.x > app.WIDTH:
                self.bullets.remove(bullet)
                
        self.animation_timer += 1
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            frames = self.animations[self.state]
            self.frame_index = (self.frame_index + 1) % len(frames)
            self.image = frames[self.frame_index]
            center = self.rect.center
            self.rect = self.image.get_rect()
            self.rect.center = center
        pass

    def draw(self, surface):
        """Draw the player on the screen."""
        if self.facing_left:
            flipped = pygame.transform.flip(self.image,True,False)
            surface.blit(flipped,self.rect)
        else:
            surface.blit(self.image,self.rect)

        for bullet in self.bullets:
            bullet.draw(surface)

    def take_damage(self, amount):
        """Reduce the player's health by a given amount, not going below zero."""
        self.health = max(0, self.health - amount)
        pass

    def shoot_toward_position(self, tx, ty):
        if self.shoot_timer >= self.shoot_cooldown:
            return

        dx = tx - self.x
        dy = ty - self.y
        dist = math.sqrt(dx**2 + dy**2)
        if dist == 0:
            return

        vx = (dx / dist) * self.bullet_speed
        vy = (dy / dist) * self.bullet_speed

        angle_spread = 10
        base_angle = math.atan2(vy, vx)
        mid = (self.bullet_count - 1) / 2

        for i in range(self.bullet_count):
            offset = i - mid
            spread_radians = math.radians(angle_spread * offset)
            angle = base_angle + spread_radians

            final_vx = math.cos(angle) * self.bullet_speed
            final_vy = math.sin(angle) * self.bullet_speed
            bullet = Bullet(self.x, self.y, final_vx, final_vy, self.bullet_size)
            self.bullets.append(bullet)
        self.shoot_timer = 0

    def circleshot(self):
        num=15
        deg = math.radians(360/num)
        for x in range(0,num):
            bullet = Bullet(self.x,self.y,math.cos(x*deg)*self.bullet_speed*0.5,math.sin(x*deg)*self.bullet_speed*0.5,self.bullet_size)
            self.bullets.append(bullet)


    def shoot_toward_mouse(self, pos):
        mx, my = pos # m denotes mouse
        self.shoot_toward_position(mx, my)

    def shoot_toward_enemy(self, enemy):
        self.shoot_toward_position(enemy.x, enemy.y)
    def teleport(self,posx,posy):
        #add upward floating particle circular transition(blue)
        self.x=posx
        self.y=posy

    def shootbeam(self, posx, posy):
        # Calculate angle between player and target position
        angle_rad = math.atan2(posy - self.y, posx - self.x)
        angle_deg = math.degrees(angle_rad)
        initial_beam_width = 25  # Starting width of the beam
        beam_start_x = self.x + (math.cos(angle_rad) * 470)
        beam_start_y = self.y + (math.sin(angle_rad) * 470)
        # Store beam information
        self.beam_display = [
            angle_deg,           
            beam_start_x,        
            beam_start_y,       
            30,                  
            True,                
        ]