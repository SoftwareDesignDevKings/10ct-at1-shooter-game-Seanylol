import pygame,math,app,random,time

class Spike:
    def __init__(self, position,timer,rect,active):
        self.assets = app.load_assets()
        self.pos = position
        self.timer = timer
        self.rect = rect
        self.active = active
        self.img = pygame.transform.scale(self.assets["spike"][0],(app.TW,app.TW))        #obtains the spike image from assets and resizes to tile dimensions

    def update(self,dt):
        self.timer -= dt
        # Check if spike has become active
        if self.timer <= 0 and self.timer > -2:
            self.active = True
        # Mark for removal if lifetime is up
        if self.timer <= -2:
            self.active=False

    def drw(self,surface):
        print(self.active)
        if self.timer> 0:
            # 1.Draw warning indicator to provide reaction time
            # 2.Create a surface for the warning rectangle
            warning_rect = pygame.Rect(self.pos[0], self.pos[1], app.TW, app.TW)
            alpha = int(255 * (1 - self.timer))  # Fade in effect
            warning_color = (255, 0, 0, min(255, max(0, alpha)))
            warning_surface = pygame.Surface((app.TW, app.TW), pygame.SRCALPHA)
            pygame.draw.rect(warning_surface, warning_color, warning_surface.get_rect(), 2)
            surface.blit(warning_surface, (self.pos[0], self.pos[1]))
        elif self.active:
            surface.blit(self.img, self.pos)

'''
                row_spikes.append({
                    'position': [pos_x, pos_y],
                    'timer': current_timer,
                    'rect': spike_rect,
                    'active': False
                })
                '''