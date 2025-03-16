# app.py
import pygame
import os

# --------------------------------------------------------------------------
#                               CONSTANTS
# --------------------------------------------------------------------------

WIDTH = 800
HEIGHT = 600
FPS = 60

PLAYER_SPEED = 3
DEFAULT_ENEMY_SPEED = 1

SPAWN_MARGIN = 50
ENEMY_SCALE_FACTOR = 2
PLAYER_SCALE_FACTOR = 2
FLOOR_TILE_SCALE_FACTOR = 2
HEALTH_SCALE_FACTOR = 3

PUSHBACK_DISTANCE = 80
ENEMY_KNOCKBACK_SPEED = 5
TW=16

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720


# --------------------------------------------------------------------------
#                       ASSET LOADING FUNCTIONS
# --------------------------------------------------------------------------

def load_frames(prefix, frame_count, scale_factor, folder="assets"):
    frames = []
    for i in range(frame_count):
        #string formatting: allows convenient access
        image_path = os.path.join(folder, f"{prefix}_{i}.png")
        img = pygame.image.load(image_path).convert_alpha()
        if scale_factor != 1:
            w = img.get_width() * scale_factor
            h = img.get_height() * scale_factor
            if prefix=='lava':  
                img = pygame.transform.scale(img, (TW, TW))
            else:
                img=pygame.transform.scale(img,(w,h))

        frames.append(img)
    return frames

def load_floor_tiles(folder="assets"):
    floor_tiles = []
    for i in range(8):
        #8 is simply the number of images uploaded
        path = os.path.join(folder, f"floor_{i}.png")
        tile = pygame.image.load(path).convert()

        if FLOOR_TILE_SCALE_FACTOR != 1:
            tw = tile.get_width() * FLOOR_TILE_SCALE_FACTOR
            th = tile.get_height() * FLOOR_TILE_SCALE_FACTOR
            tile = pygame.transform.scale(tile, (tw, th))

        floor_tiles.append(tile)
    return floor_tiles

def load_assets():
    #2d dictionary
    assets = {}

    # Enemies
    assets["enemies"] = {
        "orc":    load_frames("orc",    4, scale_factor=ENEMY_SCALE_FACTOR),
        "undead": load_frames("undead", 4, scale_factor=ENEMY_SCALE_FACTOR),
        "demon":  load_frames("demon",  4, scale_factor=ENEMY_SCALE_FACTOR*0.8),#tweak stuff here
        #add new objects: should not be that hard

    }

    # Player
    assets["player"] = {
        "idle": load_frames("player_idle", 4, scale_factor=PLAYER_SCALE_FACTOR),
        "run":  load_frames("player_run",  4, scale_factor=PLAYER_SCALE_FACTOR),
    }

    assets["floor_tiles"] = load_floor_tiles()
    assets["lava"]=load_frames("lava",1,scale_factor=PLAYER_SCALE_FACTOR)
    # Floor tiles
    assets["flesh"]=load_frames("flesh",1,scale_factor=ENEMY_SCALE_FACTOR)
    # Health images
    assets["health"] = load_frames("health", 6, scale_factor=HEALTH_SCALE_FACTOR)

    # Example coin image (uncomment if you have coin frames / images)
    # assets["coin"] = pygame.image.load(os.path.join("assets", "coin.png")).convert_alpha()

    return assets