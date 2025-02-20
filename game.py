# game.py
import pygame
import random
import os

import app

class Game:
    def __init__(self):
        pygame.init()  # Initialize Pygame
        # TODO: Create a game window using Pygame
        # self.screen = ?

        # TODO: Set up the game clock for frame rate control
        # self.clock = ?

        # TODO: Load assets (e.g., fonts, images)
        # self.font_small = ?

        # TODO: Set up game state variables
        # self.running = True

        # TODO: Create a random background
        # self.background = ?
        
    def reset_game(self):
        self.game_over = False

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
            pass
            # TODO: Set a frame rate limit
            # self.clock.tick( ? )

            # TODO: Handle player input and events
            # self.handle_events()

            # TODO: Update game objects
            # self.update()

            # TODO: Draw everything on the screen
            # self.draw()

        pygame.quit()

    def handle_events(self):
        """Process user input (keyboard, mouse, quitting)."""

        for event in pygame.event.get():
            pass
            # TODO: Allow the player to quit the game
            # if event.type == ?:
            #     self.running = False

    def update(self):
        """Update the game state (player, enemies, etc.)."""
        pass

    def draw(self):
        """Render all game elements to the screen."""
        pass
        # TODO: Draw the background
        # self.screen.blit(?, (0, 0))

        # TODO: Draw player, enemies, UI elements

        # Refresh the screen
        pygame.display.flip()