import app
import pygame
class Coin:
    def __init__(self, x, y,tpe):
        self.x = x
        self.y = y
        self.tpe = tpe
        self.assets = app.load_assets()
        self.rect=pygame.Rect(0,0,0,0)

    def draw(self, surface):
        surf = app.pygame.Surface((15,15),app.pygame.SRCALPHA)
        if self.tpe==-1:
            surf.fill((255, 215, 0))
        else:
            surf = pygame.transform.scale(self.assets['powerups'][self.tpe],(15,15))
        self.rect = surf.get_rect(center=(self.x, self.y))
        surface.blit(surf, self.rect)
