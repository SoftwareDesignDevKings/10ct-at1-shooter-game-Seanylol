#!/usr/bin/python3.4
# Setup Python ----------------------------------------------- #
import pygame, sys, random, math,app
# Setup pygame/window ---------------------------------------- #
mainClock = pygame.time.Clock()
from pygame.locals import *
pygame.init()
pygame.display.set_caption('Recursive Particle Explosion')
screen = pygame.display.set_mode((800, 600), 0, 32)
particles = []

# Color palette
COLORS = [
    (255, 0, 0),      # Red
    (255, 127, 0),    # Orange
    (255, 255, 0),    # Yellow
    (255, 200, 100),  # Light orange
]

# Explosion effect:
def spawn_explosion(origin, size, color_index, vel, splitnum, pos):
    """
    Creates a recursive explosion of particles
    origin: original center of explosion
    size: size of particles
    color_index: index in the COLORS array
    vel: velocity factor
    splitnum: number of particles to split into
    pos: current position
    """
    if size < 2:  # Base case - stop recursion when particles get too small
        return
    
    # Create particles in a circular pattern
    for x in range(splitnum):
        # Calculate angle in radians (not degrees)
        angle = math.radians(x * (360 / splitnum))
        
        # Calculate offset from center
        offset_x = (size/2) * math.cos(angle)
        offset_y = (size/2) * math.sin(angle)
        
        # Calculate center position of new particle
        center = [pos[0] + offset_x, pos[1] + offset_y]
        
        # Calculate direction vector from origin to center
        dir_x = center[0] - origin[0]
        dir_y = center[1] - origin[1]
        
        # Normalize direction vector (avoid division by zero)
        mag = math.sqrt(dir_x**2 + dir_y**2)
        if mag == 0:
            dir_x, dir_y = random.uniform(-1, 1), random.uniform(-1, 1)
        else:
            dir_x, dir_y = dir_x/mag, dir_y/mag
        
        # Add randomness to velocity
        vel_factor = vel * random.uniform(0.8, 1.2)
        velocity = [dir_x * vel_factor, dir_y * vel_factor]
        
        # Add particle with lifetime proportional to size
        lifetime = random.uniform(size*0.8, size*1.2)
        particles.append({
            'pos': center,
            'vel': velocity,
            'size': size,
            'color': COLORS[color_index % len(COLORS)],
            'lifetime': lifetime,
            'max_lifetime': lifetime,
            'origin': origin
        })
        
        # Recursive call with smaller size, different color, reduced velocity
        if random.random() < 0.3:  # Only some particles spawn children (probabilistic)
            new_color = (color_index + 1) % len(COLORS)
            spawn_explosion(origin, size*0.6, new_color, vel*0.7, max(3, splitnum-1), center)



def create_explosion(pos, size=23, particles_count=8):
    """Helper function to create an explosion at the given position"""
    spawn_explosion(pos, size, 0, 3.0, particles_count, pos)

assets = app.load_assets()
flesh = assets["flesh"][0]
# Loop ------------------------------------------------------- #
last_explosion = 0
while True:
    # Timing
    dt = mainClock.tick(60) / 1000.0  # Convert to seconds
    
    # Background --------------------------------------------- #
    screen.fill((0, 0, 0))
    mx, my = pygame.mouse.get_pos()
    particles_to_remove = []
    for particle in particles:
        # Update position
        particle['pos'][0] += particle['vel'][0]
        particle['pos'][1] += particle['vel'][1]
        
        # Apply gravity (optional)
        particle['vel'][1] += 0.2
        particle['vel'][0] *= 0.98
        particle['vel'][1] *= 0.98
        particle['lifetime'] -= dt * 30
        
        # Calculate size and opacity based on remaining lifetime
        fade_ratio = particle['lifetime'] / particle['max_lifetime']
        current_size = max(0, particle['size'] * fade_ratio)
        
        # Draw particle
        if fade_ratio > 0:
            # Get base color and apply fading
            r, g, b = particle['color']
            color = (r, g, b, int(255 * fade_ratio))
            dx = particle['origin'][0]-particle['pos'][0]
            dy = (particle['origin'][1]-particle['pos'][1])*-1
            angle = math.degrees(math.atan2(dy,dx))
            img = pygame.transform.rotate(pygame.transform.scale(flesh,(current_size,current_size)),angle-45)
            rect = img.get_rect(center=(particle['pos'][0]+current_size//2,particle['pos'][1]+current_size//2))
            screen.blit(img,rect.topleft)

            #this legit works
            # Draw circle
            
            pygame.draw.circle(
                screen, 
                color, 
                [int(particle['pos'][0]), int(particle['pos'][1])], 
                int(current_size/3)
            )
            
            
        
        # Mark for removal if lifetime expired
        if particle['lifetime'] <= 0:
            particles_to_remove.append(particle)
    
    # Remove dead particles
    for particle in particles_to_remove:
        if particle in particles:
            particles.remove(particle)
    
    # Event handling
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                pygame.quit()
                sys.exit()
        if event.type == MOUSEBUTTONDOWN:
            create_explosion((mx, my), 20, 8)
    
    # Create explosions on mouse click or randomly
    current_time = pygame.time.get_ticks()
    if pygame.mouse.get_pressed()[0] and current_time - last_explosion > 100:
        create_explosion((mx, my), random.uniform(15, 25), random.randint(6, 12))
        last_explosion = current_time
    
    # Display info
    font = pygame.font.SysFont(None, 24)
    text = font.render(f"Particles: {len(particles)}", True, (255, 255, 255))
    screen.blit(text, (10, 10))
    
    # Update display
    pygame.display.update()