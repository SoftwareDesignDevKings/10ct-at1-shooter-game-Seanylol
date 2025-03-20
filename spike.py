import pygame
import app
import math
import time
import random

pygame.init()
screen = pygame.display.set_mode((app.SCREEN_WIDTH, app.SCREEN_HEIGHT))
pygame.display.set_caption("Working With Images")
clock = pygame.time.Clock()

BG = (255, 255, 255)
BLACK = (0, 0, 0)
assets = app.load_assets()
spike = assets["spike"][0]
spike = pygame.transform.scale(spike,(app.TW,app.TW))
rects = [spike.get_rect(), spike.get_rect()]

'''
width = app.FLOOR_TILE_SCALE_FACTOR//2
poses = [[width, width], [app.SCREEN_WIDTH//2-width, app.SCREEN_HEIGHT//2-width]]
run = True
rows = []
'''

def generate_random_wall_region(center_point, max_rows, radius):
    timer_start = 1.0  # Initial delay before showing spike
    tile_size = app.TW  # Tile width
    center_grid_x = (center_point[0] // tile_size) * tile_size
    center_grid_y = (center_point[1] // tile_size) * tile_size
    # Whole number division will clamp the generation points to corners
    max_grid_distance = radius // tile_size
    num_rows = random.randint(max_rows // 2, max_rows)
    occupied_positions = set()
    for _ in range(num_rows):
        y_offset = random.randint(-max_grid_distance, max_grid_distance)
        row_y = center_grid_y + (y_offset * tile_size)
        if row_y < 0 or row_y >= app.SCREEN_HEIGHT:
            continue
        x_offset = random.randint(-max_grid_distance, max_grid_distance)
        start_x = center_grid_x + (x_offset * tile_size)
        max_length = random.randint(1, 7)  
        if start_x < 0:
            start_x = 0
        if start_x + (max_length * tile_size) > app.SCREEN_WIDTH:
            max_length = (app.SCREEN_WIDTH - start_x) // tile_size
        if max_length <= 0:
            continue
        
        row_positions = []
        can_place = True
        for i in range(max_length):
            pos_x = start_x + (i * tile_size)
            pos_y = row_y
            pos_key = (pos_x, pos_y)
            if pos_key in occupied_positions:
                can_place = False
                break
            # Increase the timer for each spike to create a sequential appearance
            current_timer = timer_start + (i * 0.1)
            row_positions.append([[pos_x, pos_y], current_timer])
        
        if can_place and row_positions:
            for pos in row_positions:
                occupied_positions.add((pos[0][0], pos[0][1]))
            rows.append(row_positions)
            # Increase the timer start for the next row for staggered appearance
            timer_start += 0.2

while run:
    dt = clock.tick(60)/1000
    screen.fill(BLACK)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
            generate_random_wall_region([x, y], 15, radius=40)
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_c:
                rows = []
    
    for row_index, row in enumerate(rows[:]):
        positions_to_remove = []
        for position_index, position in enumerate(row):
            position[1] -= dt
            if position[1] > 0:
                warning_rect = pygame.Rect(position[0][0], position[0][1], app.TW, app.TW)
                alpha = int(255 * (1 - position[1]))  # Fade in effect
                pygame.draw.rect(screen, (255, 0, 0, min(255, max(0, alpha))), warning_rect, 2)
            elif position[1] <= -2:  
                positions_to_remove.append(position_index)
            else:
                screen.blit(spike, position[0])
        for index in sorted(positions_to_remove, reverse=True):
            row.pop(index)
        
        if not row:
            rows[row_index] = None
    rows = [row for row in rows if row is not None]
    
    pygame.display.update()

pygame.quit()