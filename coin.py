import app
import pygame
class Coin:
    def __init__(self, x, y,tpe):
        #store x y position and type for incorporating powerups
        self.x = x
        self.y = y
        self.tpe = tpe
        self.assets = app.load_assets()#assets loading
        self.rect=pygame.Rect(0,0,0,0)#creates default rectnagle

    def draw(self, surface):
        surf = app.pygame.Surface((15,15),app.pygame.SRCALPHA)
        if self.tpe==-1:
            surf.fill((255, 215, 0))# draws yellow square 15 by 15 if it is a coin
        else:
            surf = pygame.transform.scale(self.assets['powerups'][self.tpe],(15,15))#else blits a rescaled powerup icon in the same location
        self.rect = surf.get_rect(center=(self.x, self.y))
        surface.blit(surf, self.rect)
