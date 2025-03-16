import pygame
import app
import math
import time

pygame.init()
screen = pygame.display.set_mode((app.SCREEN_WIDTH, app.SCREEN_HEIGHT))
pygame.display.set_caption("Working With Images")
BG = (255, 255, 255)
BLACK = (0, 0, 0)
assets = app.load_assets()
flesh = assets["flesh"][0]
flesh2 = pygame.transform.scale(flesh, (100, 100))
flesh3 = pygame.transform.rotate(flesh2, 45)

# Create original image copies to maintain quality during rotations
original_images = [flesh2.copy(), flesh2.copy()]
rects = [flesh2.get_rect(), flesh3.get_rect()]
angles = [0, 45]  # Starting angles
poses = [[50, 50], [app.SCREEN_WIDTH//2-50, app.SCREEN_HEIGHT//2-50]]

run = True
print(app.SCREEN_HEIGHT)

while run:
    screen.fill(BLACK)
    
    # Display images with current rotation
    for i in range(2):
        rotated_image = pygame.transform.rotate(original_images[i], angles[i])
        # Get the rect of the rotated image and center it at the original position
        rotated_rect = rotated_image.get_rect(center=(poses[i][0] + 50, poses[i][1] + 50))
        screen.blit(rotated_image, rotated_rect.topleft)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
            print(pygame.mouse.get_pos())
            for i in range(2):
                # Calculate angle to mouse position from center of image
                dx = x - (poses[i][0] +50)
                dy = y - (poses[i][1] + 50)
                new_angle = math.degrees(math.atan2(-dy, dx))  # Y is inverted in pygame
                angles[i] = new_angle
                
    pygame.display.update()

pygame.quit()