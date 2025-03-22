#!/usr/bin/python3.4
# Setup Python ----------------------------------------------- #
import pygame, sys, random
 
# Setup pygame/window ---------------------------------------- #
mainClock = pygame.time.Clock()
from pygame.locals import *
pygame.init()
pygame.display.set_caption('Blue Flame Effect')
screen = pygame.display.set_mode((500, 500),0,32)
 
# Particle system for the blue flame effect
particles = []
 
# Loop ------------------------------------------------------- #
while True:
    
    # Background --------------------------------------------- #
    screen.fill((0,0,0))
    mx, my = pygame.mouse.get_pos()
    # Generate particles at mouse position
    for i in range(3): 

        vel_x = random.uniform(-0.8, 0.8)
        vel_y = random.uniform(-3, -0.5)  # Negative values make particles go up

        size = random.uniform(2, 5)
        blue_shade = random.randint(0, 255)  # Varying blue intensity
        particles.append([
            [mx, my],  # Position at mouse
            [vel_x, vel_y],  # Velocity
            size,  # Size
            (20, 50, blue_shade),  # Color (blue flame with varying intensity)
            random.uniform(0.8, 1.2)  # Lifetime factor (for varying duration)
        ])
 
    # Update and draw particles
    for particle in particles[:]:  # Use a copy for safe removal
        # Update position
        particle[0][0] += particle[1][0]
        particle[0][1] += particle[1][1]
        
        particle[2] -= 0.1 * particle[4] 
        particle[1][1] -= 0.02
        
        # Narrow the spread as particles rise (key change)
        # Calculate how far the particle has traveled from its origin
        distance_from_origin = my - particle[0][1]
        if distance_from_origin > 10:  # Only apply narrowing after particles have moved a bit
            # Pull particles toward center over time (stronger effect as they rise higher)
            narrowing_strength = 0.03 * (distance_from_origin / 50)
            if particle[0][0] > mx:
                particle[1][0] -= narrowing_strength
            else:
                particle[1][0] += narrowing_strength
        
        # Add a slight randomization for flickering, but less than before
        particle[1][0] += random.uniform(-0.05, 0.05)
        
        # Draw the particle as a circle with its color and size
        if particle[2] > 0:
            pygame.draw.circle(
                screen, 
                particle[3], 
                [int(particle[0][0]), int(particle[0][1])], 
                int(particle[2])
            )
        
        # Remove particles that have faded out
        if particle[2] <= 0:
            particles.remove(particle)
    
    # Buttons ------------------------------------------------ #
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                pygame.quit()
                sys.exit()
                
    # Update ------------------------------------------------- #
    pygame.display.update()
    mainClock.tick(60)