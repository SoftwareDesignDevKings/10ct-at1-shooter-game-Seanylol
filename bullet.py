import app
class Bullet:
    def __init__(self, x, y, vx, vy, size):
        #tracks position, x y velocity and size
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.size = size
        #creates and image surface
        self.image = app.pygame.Surface((self.size, self.size), app.pygame.SRCALPHA)
        self.image.fill((255, 255, 255))
        self.rect = self.image.get_rect(center=(self.x, self.y))
        
    def update(self):
        #adding velocity to position, also redrawing the bounding rect
        self.x += self.vx
        self.y += self.vy
        self.rect.center = (self.x, self.y)
    def draw(self, surface):
        #draws the rectangle onto the image surface 
        surface.blit(self.image, self.rect)