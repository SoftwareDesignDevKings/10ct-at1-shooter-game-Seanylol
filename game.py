# game.py
import pygame
import random
import os
import math
from player import Player
from enemy import Enemy
#feature changes: physics simulation for player, obstacles/level difficulty increase, wave attacks, bombing
#i.e explosions/blood splatter, projectile trail
#The surface can also be changed, i.e ice spreading/slow barrier

'''
class feature:
    def __init__(self):
        pass
    dx=[1,0,-1,0]
    dy=[0,1,0,-1]
    def generate(self,type,depth):
        pos=[]
        for x in range(len(pos)){
            for y in range(4):
                nx = 
        }
        #this will randomise environment geeration. some can also add damage: add in player class
        pass
'''

#try to find cool fractal pattenrs for explosion effects/make them yourself recursively
import app

class Game:
    def __init__(self):
        pygame.init()  # Initialize Pygame
        self.screen = pygame.display.set_mode((app.WIDTH,app.HEIGHT))
        pygame.display.set_caption("Sean's shooter game")
        self.clock = pygame.time.Clock()#basically creating an inbuilt object
        self.assets= app.load_assets()
        font_path = os.path.join("assets","PressStart2P.ttf")
        self.font_small = pygame.font.Font(font_path,18)
        self.font_large = pygame.font.Font(font_path,32) #second pa
        self.background = self.create_random_background(app.WIDTH,app.HEIGHT,self.assets["floor_tiles"])
        self.running = True
        self.game_over=False

        self.enemies = []
        self.enemy_spawn_timer = 0
        self.enemy_spawn_interval = 60
        self.enemies_per_spawn = 1

        self.reset_game()

        
        
    def reset_game(self):
        self.player = Player(app.WIDTH//2,app.HEIGHT//2,self.assets)
        self.enemies = []
        self.enemy_spawn_timer = 0
        self.enemies_per_spawn = 1
        self.game_over = False

    def create_random_background(self, width, height, floor_tiles):
        bg = pygame.Surface((width, height))
        tile_w = floor_tiles[0].get_width()
        tile_h = floor_tiles[0].get_height()

        for y in range(0, height, tile_h):
            for x in range(0, width, tile_w):
                tile = random.choice(floor_tiles)
                #This defines the color scheme: good enough for background but if you want to make more complex landscapes like cactus or connected walls you need to implement something more complex
                bg.blit(tile, (x, y))

        return bg

    def run(self):
        while self.running:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_x]:
                pygame.quit()
            # TODO: Set a frame rate limit
            self.clock.tick(app.FPS)
            # TODO: Handle player input and events
            self.handle_events()
            if (not self.game_over):
                self.update()
            else:
                #display gameover message
                '''
                if keys[pygame.K_r]:
                    self.reset_game
                    self.running=True
                if keys[pygame.K_x]:
                    pygame.quit()
                '''
            self.draw()

    def draw_game_over_screen(self):
            # Dark overlay
            overlay = pygame.Surface((app.WIDTH, app.HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))

            # Game Over text
            game_over_surf = self.font_large.render("GAME OVER!", True, (255, 0, 0))
            game_over_rect = game_over_surf.get_rect(center=(app.WIDTH // 2, app.HEIGHT // 2 - 50))
            self.screen.blit(game_over_surf, game_over_rect)

            # Prompt to restart or quit
            prompt_surf = self.font_small.render("Press R to Play Again or ESC to Quit", True, (255, 255, 255))
            prompt_rect = prompt_surf.get_rect(center=(app.WIDTH // 2, app.HEIGHT // 2 + 20))
            self.screen.blit(prompt_surf, prompt_rect)
            
    def handle_events(self):
        """Process user input (keyboard, mouse, quitting)."""
        for event in pygame.event.get():
            # TODO: Allow the player to quit the game
            if event.type == pygame.quit:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if self.game_over:
                    if event.key == pygame.K_r:
                        self.reset_game()
                    elif event.key == pygame.K_ESCAPE:
                        self.running = False
                else:
                    if event.key == pygame.K_SPACE:
                        nearest_enemy = self.find_nearest_enemy()
                        if nearest_enemy:
                            self.player.shoot_toward_enemy(nearest_enemy)
                    if event.key==pygame.K_c:
                        self.player.circleshot()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    self.player.shoot_toward_mouse(event.pos)

    def update(self):
        self.player.handle_input()
        self.player.update()
        for enemy in self.enemies:
            enemy.update(self.player)
        self.check_player_enemy_collisions()
        self.check_bullet_enemy_collisions()
        if self.player.health <= 0:
            print("pass")
            self.game_over = True
            return 
        self.spawn_enemies()
        
    def draw(self):
        """Render all game elements to the screen."""

        self.screen.blit(self.background, (0, 0))
        if not self.game_over:
            self.player.draw(self.screen)
        else:
            self.draw_game_over_screen()
        for enemy in self.enemies:
            enemy.draw(self.screen)
        hp = max(0, min(self.player.health, 5))
        health_img = self.assets["health"][hp]
        self.screen.blit(health_img, (10, 10))
        pygame.display.flip()

    def spawn_enemies(self):
        self.enemy_spawn_timer += 1
        if self.enemy_spawn_timer >= self.enemy_spawn_interval:
            self.enemy_spawn_timer = 0

            for _ in range(self.enemies_per_spawn):
                side = random.choice(["top", "bottom", "left", "right"])
                if side == "top":
                    x = random.randint(0, app.WIDTH)
                    y = -app.SPAWN_MARGIN
                elif side == "bottom":
                    x = random.randint(0, app.WIDTH)
                    y = app.HEIGHT + app.SPAWN_MARGIN
                elif side == "left":
                    x = -app.SPAWN_MARGIN
                    y = random.randint(0, app.HEIGHT)
                else:
                    x = app.WIDTH + app.SPAWN_MARGIN
                    y = random.randint(0, app.HEIGHT)

                enemy_type = random.choice(list(self.assets["enemies"].keys()))
                enemy = Enemy(x, y, enemy_type, self.assets["enemies"])
                self.enemies.append(enemy)

    def check_player_enemy_collisions(self):
        collided = False
        for enemy in self.enemies:
            if enemy.rect.colliderect(self.player.rect):
                collided = True
                break

        if collided:
            self.player.take_damage(1)
            px, py = self.player.x, self.player.y
            for enemy in self.enemies:
                enemy.set_knockback(px, py, app.PUSHBACK_DISTANCE)

    def find_nearest_enemy(self):
        if not self.enemies:
            return None
        nearest = None
        min_dist = float('inf')
        px, py = self.player.x, self.player.y
        for enemy in self.enemies:
            dist = math.sqrt((enemy.x - px)**2 + (enemy.y - py)**2)
            if dist < min_dist:
                min_dist = dist
                nearest = enemy
        return nearest
    
    def check_bullet_enemy_collisions(self):
        for bullet in self.player.bullets:
            for enemy in self.enemies:
                if bullet.rect.colliderect(enemy.rect):
                    self.player.bullets.remove(bullet)
                    self.enemies.remove(enemy)

