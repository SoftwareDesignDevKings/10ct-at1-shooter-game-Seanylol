import pygame
import random
import os
import math
from player import Player
from enemy import Enemy
from coin import Coin
#feature changes: physics simulation for player, obstacles/level difficulty increase, wave attacks, bombing
#i.e explosions/blood splatter, projectile trail
#The surface can also be changed, i.e ice spreading/slow barrier
#try to find cool fractal pattenrs for explosion effects/make them yourself recursively
import app

COLORS = [
    (255, 0, 0),      # Red
    (255, 127, 0),    # Orange
    (255, 255, 0),    # Yellow
    (255, 200, 100),  # Light orange
]

class Game:
    def __init__(self):
        pygame.init()  # Initialize Pygame
        self.screen = pygame.display.set_mode((app.WIDTH, app.HEIGHT))
        pygame.display.set_caption("Sean's shooter game")
        self.clock = pygame.time.Clock()  # basically creating an inbuilt object
        self.assets = app.load_assets()
        font_path = os.path.join("assets", "PressStart2P.ttf")
        self.font_small = pygame.font.Font(font_path, 18)
        self.font_large = pygame.font.Font(font_path, 32)  # second pa
        self.background = self.create_random_background(app.WIDTH, app.HEIGHT, self.assets["floor_tiles"])
        self.running = True
        self.game_over = False
        self.coins = []
        self.enemies = []
        self.enemy_spawn_timer = 0
        self.enemy_spawn_interval = 60
        self.enemies_per_spawn = 1
        self.blocks = []
        self.spike_rows = []
        self.blockind = 0
        self.particles = []
        self.float_particles=[]
        self.particles_surface = pygame.Surface((app.WIDTH, app.HEIGHT), pygame.SRCALPHA)
        self.last_update_time = pygame.time.get_ticks()
        self.reset_game()
        self.spike_cooldown = 10
        self.spike_timer = 0
        self.enemy_speed=1
        #powerups

        self.power_up_freq=0.5

        self.tp=0
        self.bm=0
        self.spreadshots=0
        self.tped=False
        self.beamed=False

        self.lv=1
        self.levels = [[self.player.shoot_cooldown,5],[self.spike_cooldown,1.5],[self.enemy_spawn_interval,-10],[self.enemy_speed,2]],

        #continuously apply 
        self.ba=False
        self.beamangle = 0




    def spawn_flame(self, pos, color,dir):
        # Create more varied movement by using both x and y components
        #original ranges, -0.8 to 0.8, -3 to -0.3
        vel_x = dir[0]+random.uniform(-0.5, 0.5)
        vel_y = dir[1]+random.uniform(-0.8, 0.5)  
        size = random.uniform(2, 5)
        r,g,b= color
        red = random.randint(0, 255)  # Varying blue intensity
        self.particles.append({
                'pos': pos,
                'vel': [vel_x,vel_y],
                'size': size,
                'color':(red, g, b),  
                'lifetime': random.uniform(30.0,40.2),
                'max_lifetime': random.uniform(30.0,40.2),
                'origin': [-1,-1],
                'type': 0
        }
        )

    def check_lvlup(self):
        if self.player.xp > 3**self.lv:
            self.lv += 1
            self.level_up_text = {
                'text': f"LEVEL {self.lv}",
                'timer': 3.0,  
                'start_time': pygame.time.get_ticks() / 1000.0,  
                'alpha': 255
            }
            level_improvements = [5,-1.5,-10,3]
            #continnuously apply level changes: this makes the game exponentially challenging
            # a pointer may allow sparing if statements but im not yet familair with them so no
            for i in range(len(level_improvements)):
                c = level_improvements[i]
                if i == 0:
                    self.player.shoot_cooldown += c
                elif i == 1:
                    self.spike_cooldown += c
                elif i == 2:
                    self.enemy_spawn_interval += c
                elif i == 3:
                    self.enemy_speed += c
            self.power_up_freq-=-0.1
            self.player.speed-=1
            

    def spawn_explosion(self, origin, size, color_index, vel, splitnum, pos,fleshtype):
        if size < 2:  # Base case - stop recursion when particles get too small
            return
        for x in range(splitnum):
            angle = math.radians(x * (360 / splitnum))

            offset_x = (size/2) * math.cos(angle)
            offset_y = (size/2) * math.sin(angle)
            center = [pos[0] + offset_x, pos[1] + offset_y]

            dir_x = center[0] - origin[0]
            dir_y = center[1] - origin[1]

            mag = math.sqrt(dir_x**2 + dir_y**2)
            if mag == 0:
                dir_x, dir_y = random.uniform(-1, 1), random.uniform(-1, 1)
            else:
                dir_x, dir_y = dir_x/mag, dir_y/mag
            
            vel_factor = vel * random.uniform(0.8, 1.2)
            velocity = [dir_x * vel_factor, dir_y * vel_factor]
        
            lifetime = random.uniform(size*0.8, size*1.2)
            self.particles.append({
                'pos': center,
                'vel': velocity,
                'size': size,
                'color': COLORS[color_index % len(COLORS)],
                'lifetime': lifetime,
                'max_lifetime': lifetime,
                'origin': origin,
                'type': fleshtype
            })
            
            if random.random() < 0.3:
                new_color = (color_index + 1) % len(COLORS)
                self.spawn_explosion(origin, size*0.6, new_color, vel*0.7, max(3, splitnum-1), center,fleshtype)

    def create_explosion(self, pos, size=23, particles_count=8,fleshtype=0):
        """Helper function to create an explosion at the given position"""
        self.spawn_explosion(pos, size, 0, 3.0, particles_count, pos,fleshtype)

    def generate_random_wall_region(self, center_point, max_rows, radius):
        timer_start = 1.0  
        tile_size = app.TW  
        center_grid_x = (center_point[0] // tile_size) * tile_size
        center_grid_y = (center_point[1] // tile_size) * tile_size
        max_grid_distance = radius // tile_size
        num_rows = random.randint(max_rows // 2, max_rows)
        occupied_positions = set()
        
        for _ in range(num_rows):
            y_offset = random.randint(-max_grid_distance, max_grid_distance)
            row_y = center_grid_y + (y_offset * tile_size)
            if row_y < 0 or row_y >= app.HEIGHT:
                continue
                
            x_offset = random.randint(-max_grid_distance, max_grid_distance)
            start_x = center_grid_x + (x_offset * tile_size)
            max_length = random.randint(1, 7)  
            
            if start_x < 0:
                start_x = 0
            if start_x + (max_length * tile_size) > app.WIDTH:
                max_length = (app.WIDTH - start_x) // tile_size
                
            if max_length <= 0:
                continue
            
            row_spikes = []
            can_place = True
            
            for i in range(max_length):
                pos_x = start_x + (i * tile_size)
                pos_y = row_y
                pos_key = (pos_x, pos_y)
                
                if pos_key in occupied_positions:
                    can_place = False
                    break
                    
                current_timer = timer_start + (i * 0.1)
                
                # Create a proper spike object with a rect for collision detection
                spike_rect = pygame.Rect(pos_x, pos_y, tile_size, tile_size)
                row_spikes.append({
                    'position': [pos_x, pos_y],
                    'timer': current_timer,
                    'rect': spike_rect,
                    'active': False
                })
            
            if can_place and row_spikes:
                for spike in row_spikes:
                    occupied_positions.add((spike['position'][0], spike['position'][1]))
                self.spike_rows.append(row_spikes)
                timer_start += 0.2


    def reset_game(self):
        self.player = Player(app.WIDTH//2, app.HEIGHT//2, self.assets)
        self.enemies = []
        self.enemy_spawn_timer = 0
        self.enemies_per_spawn = 1
        self.game_over = False
        self.coins = []
        self.particles = []
        self.spike_rows = []
        self.spike_timer = 0


    def create_random_background(self, width, height, floor_tiles):
        bg = pygame.Surface((width, height))
        tile_w = floor_tiles[0].get_width()
        tile_h = floor_tiles[0].get_height()

        for y in range(0, height, tile_h):
            for x in range(0, width, tile_w):
                tile = random.choice(floor_tiles)
                bg.blit(tile, (x, y))

        return bg

    def run(self):
        while self.running:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_x]:
                pygame.quit()
                return

            self.clock.tick(app.FPS)
            
            # Use proper time-based updates for spike generation
            dt = self.clock.get_time() / 1000.0
            self.spike_timer += dt
            
            if self.spike_timer > self.spike_cooldown:
                self.spike_timer = 0
                x = random.randint(0, app.WIDTH)
                y = random.randint(0, app.HEIGHT)
                self.generate_random_wall_region([x, y], 15, radius=40)
                
            self.handle_events()
            self.draw()
            self.check_lvlup()
            
            if not self.game_over:
                self.update()
                

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
        # Get current mouse position for hover effect if teleport is active
        if self.tp:
            mx, my = pygame.mouse.get_pos()
            blue_color = [0, 50 + random.randint(0, 50), 200 + random.randint(0, 55)]
            self.spawn_flame([mx, my], blue_color,[0,-2.5])
        
        for event in pygame.event.get():
            if self.game_over:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.reset_game()
                    elif event.key == pygame.K_ESCAPE:
                        self.running = False
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    nearest_enemy = self.find_nearest_enemy()
                    if nearest_enemy:
                        self.player.shoot_toward_enemy(nearest_enemy)
                if event.key == pygame.K_t and self.tp>0:
                    print("Teleport mode activated")
                    self.tp -=1
                    self.tped=True
                if event.key == pygame.K_b and self.bm>0:
                    self.bm -=1
                    self.beamed=True
                if event.key == pygame.K_c and self.spreadshots>0:
                    self.player.circleshot()
                    self.spreadshots-=1
            elif event.type == pygame.KEYUP:
                # Turn off teleport mode when T key is released
                if event.key == pygame.K_t:
                    print("Teleport mode deactivated")
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if self.tped:    
                    self.player.teleport(mx, my)
                    self.tped=False
                elif self.beamed:
                    self.player.shootbeam(mx, my)
                    self.beamed=False
                    print("Beam fired")
                elif event.button == 1:  
                    self.player.shoot_toward_mouse(event.pos)



    def update(self):
        current_time = pygame.time.get_ticks()
        dt = (current_time - self.last_update_time) / 1000.0
        self.last_update_time = current_time
        
        self.player.handle_input()
        self.player.update()
        self.update_particles(dt)
        self.update_spikes(dt)
        
        for enemy in self.enemies:
            enemy.update(self.player)
            
        self.check_player_enemy_collisions()
        self.check_bullet_enemy_collisions()
        self.check_player_coin_collisions()
        self.check_player_spike_collisions()
        self.check_enemy_spike_collisions()
        
        if self.player.health <= 0:
            self.game_over = True
            return 
            
        self.spawn_enemies()
        
    def draw_level_up_text(self):
        if hasattr(self, 'level_up_text') and self.level_up_text['timer'] > 0:
            current_time = pygame.time.get_ticks() / 1000.0
            elapsed = current_time - self.level_up_text['start_time']
            if elapsed < self.level_up_text['timer']:
                alpha = int(255 * (1 - (elapsed / self.level_up_text['timer'])))
                level_text = self.font_large.render(self.level_up_text['text'], True, (255, 255, 0))
                text_surface = pygame.Surface(level_text.get_size(), pygame.SRCALPHA)
                text_surface.fill((255, 255, 255, alpha))
                level_text.blit(text_surface, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                text_rect = level_text.get_rect(center=(app.WIDTH // 2, app.HEIGHT // 2))
                self.screen.blit(level_text, text_rect)
            else:
                # Reset timer when done
                self.level_up_text['timer'] = 0

    def draw(self):
        """Render all game elements to the screen."""
        # Draw background
        self.screen.blit(self.background, (0, 0))
        
        # Draw game elements
        for coin in self.coins:
            coin.draw(self.screen)

        for x, y in self.blocks:
            self.screen.blit(self.assets["lava"][0], (x, y))
        
        # Draw spikes
        self.draw_spikes()
        
        # Draw particles
        self.draw_particles()
        
        # Draw player if not game over
        if not self.game_over:
            self.player.draw(self.screen)
        else:
            self.draw_game_over_screen()
            
        # Draw enemies
        for enemy in self.enemies:
            enemy.draw(self.screen)
            
        # Draw UI elements
        hp = max(0, min(self.player.health, 5))
        health_img = self.assets["health"][hp]
        self.screen.blit(health_img, (10, 10))
        xp_text_surf = self.font_small.render(f"XP: {self.player.xp}", True, (255, 255, 255))
        tp_text_surf = self.font_small.render(f"Teleports: {self.tp}", True, (255, 255, 255))
        bm_text_surf = self.font_small.render(f"Beams: {self.bm}", True, (255, 255, 255))
        ss_text_surf = self.font_small.render(f"Spreadshots: {self.spreadshots}", True, (255, 255, 255))

        self.screen.blit(xp_text_surf, (10, 70))
        self.screen.blit(tp_text_surf, (10, 100))
        self.screen.blit(bm_text_surf, (10, 130))
        self.screen.blit(ss_text_surf, (10, 160))
        self.draw_level_up_text()
        # Update display
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
        for enemy in self.enemies:
            if enemy.rect.colliderect(self.player.rect):
                self.player.take_damage(1)
                px, py = self.player.x, self.player.y
                for e in self.enemies:
                    e.set_knockback(px, py, app.PUSHBACK_DISTANCE)
                break

    def check_player_spike_collisions(self):
        for row in self.spike_rows:
            for spike in row:
                if spike['active'] and spike['rect'].colliderect(self.player.rect):
                        self.player.take_damage(5)
    
                    

    def check_enemy_spike_collisions(self):
        enemies_to_remove = []
        
        for row in self.spike_rows:
            for spike in row:
                if spike['active']:
                    for enemy in self.enemies:
                        if spike['rect'].colliderect(enemy.rect):
                            self.create_explosion(
                                (enemy.x, enemy.y),
                                random.uniform(15, 25),
                                random.randint(6, 12),
                                #change this later
                                0
                            )
                            # Add coin when enemy is killed by spike
                            ptype=0
                            if random.random()<self.power_up_freq:
                                ptype=random.randint(0,2)
                            else:
                                ptype = -1
                            new_coin = Coin(enemy.x, enemy.y,ptype)
                            self.coins.append(new_coin)
                            enemies_to_remove.append(enemy)
        
        for enemy in enemies_to_remove:
            if enemy in self.enemies:
                self.enemies.remove(enemy)

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
        bullets_to_remove = []
        enemies_to_remove = []
        
        # Process regular bullet collisions
        for bullet in self.player.bullets:
            self.spawn_flame([bullet.x, bullet.y], (240, 220, 15), [bullet.vx, bullet.vy])
            for enemy in self.enemies:
                if bullet.rect.colliderect(enemy.rect) and bullet not in bullets_to_remove:
                    self.create_explosion((enemy.x, enemy.y), random.uniform(15, 25), random.randint(6, 12), 0)
                    ptype=0
                    if random.random()<self.power_up_freq:
                        ptype=random.randint(0,2)
                    else:
                        ptype = -1
                    new_coin = Coin(enemy.x, enemy.y,ptype)
                    self.coins.append(new_coin)
                    bullets_to_remove.append(bullet)
                    enemies_to_remove.append(enemy)
        
        # Process beam collisions separately
        if self.ba:
            beam_angle_rad = math.radians(self.beamangle)
            beam_dir_x = math.cos(beam_angle_rad)
            beam_dir_y = math.sin(beam_angle_rad)
            beam_width = 25  # Match the width from Player.shootbeam
            for enemy in self.enemies:
                # Vector from player to enemy, expressed purely based on distance
                to_enemy_x = enemy.x - self.player.x
                to_enemy_y = enemy.y - self.player.y                
                dot_product = to_enemy_x * beam_dir_x + to_enemy_y * beam_dir_y
                
                # Skip if enemy is behind the beam (negative projection)
                if dot_product < 0:
                    continue
                
                # Calculate closest point on beam line to enemy(perpendicular distance: Dont know exactly how this works)
                closest_x = self.player.x + beam_dir_x * dot_product
                closest_y = self.player.y + beam_dir_y * dot_product
                perp_dist = math.sqrt((closest_x - enemy.x)**2 + (closest_y - enemy.y)**2)
                
                # TWeak effective beam width and check enemy overlap
                effective_width = beam_width / 2
                if perp_dist <= effective_width + enemy.rect.width / 2:
                    if enemy not in enemies_to_remove:
                        self.create_explosion((enemy.x, enemy.y), random.uniform(15, 25), random.randint(6, 12), 0)
                        ptype=0
                        if random.random()<self.power_up_freq:
                            ptype=random.randint(0,2)
                        else:
                            ptype = -1
                        new_coin = Coin(enemy.x, enemy.y,ptype)
                        self.coins.append(new_coin)
                        enemies_to_remove.append(enemy)
        
        for bullet in bullets_to_remove:
            if bullet in self.player.bullets:
                self.player.bullets.remove(bullet)
                
        for enemy in enemies_to_remove:
            if enemy in self.enemies:
                self.enemies.remove(enemy)
    
    def check_player_coin_collisions(self):
        coins_collected = []
        for coin in self.coins:
            if coin.rect.colliderect(self.player.rect):
                coins_collected.append(coin)
                if coin.tpe==-1:
                    self.player.add_xp(1)
                if coin.tpe==0:
                    self.tp+=1
                if coin.tpe==1:
                    self.bm+=1
                if coin.tpe==2:
                    self.spreadshots+=1


        for c in coins_collected:
            if c in self.coins:
                self.coins.remove(c)

    def update_particles(self, dt):
        particles_to_remove = []
        
        for particle in self.particles:

            particle['pos'][0] += particle['vel'][0]
            particle['pos'][1] += particle['vel'][1]

            particle['vel'][0] *= 0.98
            particle['vel'][1] *= 0.98
            
            if particle['origin'][0]!=-1:
                #if type is explosive
                particle['vel'][1] += 0.2

                
            particle['lifetime'] -= dt * 30
            
            # Mark for removal if lifetime is up
            if particle['lifetime'] <= 0:
                particles_to_remove.append(particle)
        
        # Remove dead particles
        for particle in particles_to_remove:
            if particle in self.particles:
                self.particles.remove(particle)
    
    def update_spikes(self, dt):
        rows_to_remove = []
        
        for row_index, row in enumerate(self.spike_rows):
            spikes_to_remove = []
            
            for spike_index, spike in enumerate(row):
                # Update timer
                spike['timer'] -= dt
                
                # Check if spike has become active
                if spike['timer'] <= 0 and spike['timer'] > -2:
                    spike['active'] = True
                
                # Mark for removal if lifetime is up
                if spike['timer'] <= -2:
                    spikes_to_remove.append(spike_index)
            
            # Remove dead spikes
            for index in sorted(spikes_to_remove, reverse=True):
                row.pop(index)
            
            # Mark empty rows for removal
            if not row:
                rows_to_remove.append(row_index)
        
        # Remove empty rows
        for index in sorted(rows_to_remove, reverse=True):
            self.spike_rows.pop(index)

    def draw_spikes(self):
        spike_img = self.assets["spike"][0]
        spike_img = pygame.transform.scale(spike_img,(app.TW,app.TW))
        
        for row in self.spike_rows:
            for spike in row:
                position = spike['position']
                
                if spike['timer'] > 0:
                    # Draw warning indicator
                    warning_rect = pygame.Rect(position[0], position[1], app.TW, app.TW)
                    alpha = int(255 * (1 - spike['timer']))  # Fade in effect
                    warning_color = (255, 0, 0, min(255, max(0, alpha)))
                    
                    # Create a surface for the warning rectangle
                    warning_surface = pygame.Surface((app.TW, app.TW), pygame.SRCALPHA)
                    pygame.draw.rect(warning_surface, warning_color, warning_surface.get_rect(), 2)
                    self.screen.blit(warning_surface, position)
                    
                elif spike['active']:
                    # Draw active spike
                    self.screen.blit(spike_img, position)
    
    def draw_particles(self):
        # Clear particles surface
        self.particles_surface.fill((0, 0, 0, 0))
        
        # Handle beam display
        self.lst = self.player.beam_display
        if self.lst[4] and self.lst[3] > 0:
            angle = self.lst[0]
            beam = pygame.transform.scale(self.assets["beam"][0], (900, self.lst[3]))
            rbeam = pygame.transform.rotate(beam, -angle)
            rec = rbeam.get_rect()
            rec.center = (self.lst[1], self.lst[2])
            self.lst[3] -= 1
            self.screen.blit(rbeam, rec)
            self.beamangle = angle
            self.ba=True
        else:
            self.ba=False
            
        for particle in self.particles:
            if particle["origin"][0] == -1:
                # For flame particles (check if color is a list before modifying)   
                # Draw the particle
                pygame.draw.circle(
                    self.particles_surface, 
                    particle["color"], 
                    (int(particle['pos'][0]), int(particle['pos'][1])), 
                    int(particle['size'])
                )
            else:
                # For explosion particles
                flesh = self.assets["flesh"][particle["type"]]
                fade_ratio = particle['lifetime'] / particle['max_lifetime']
                current_size = max(0, int(particle['size'] * fade_ratio))
                
                if fade_ratio > 0 and current_size > 0:
                    # Draw particle
                    r, g, b = particle['color']
                    color = (r, g, b, int(255 * fade_ratio))
                    
                    if flesh and current_size > 2:
                        dx = particle['origin'][0] - particle['pos'][0]
                        dy = (particle['origin'][1] - particle['pos'][1]) * -1
                        angle = math.degrees(math.atan2(dy, dx))
                        
                        # Scale and rotate flesh image
                        scaled_flesh = pygame.transform.scale(flesh, (current_size, current_size))
                        rotated_flesh = pygame.transform.rotate(scaled_flesh, angle - 45)
                        rect = rotated_flesh.get_rect(center=(particle['pos'][0], particle['pos'][1]))
                        self.particles_surface.blit(rotated_flesh, rect.topleft)
                    
                    # Circular infill
                    pygame.draw.circle(
                        self.particles_surface, 
                        color, 
                        (int(particle['pos'][0]), int(particle['pos'][1])), 
                        int(current_size/3)
                    )
        
        # Blit particles surface to screen - this should be outside the loop!
        self.screen.blit(self.particles_surface, (0, 0))