import pygame

class display:
    
    def __init__(self, x, y):
        self.x = x
        self.y = y

        self.window_x = 256
        self.window_y = 128

        if (self.window_x / self.window_y) > (self.x / self.y):
            self.pixel_size = self.window_y / self.y
        else:
            self.pixel_size = self.window_x / self.x
        
        self.screen = pygame.display.set_mode((self.window_x, self.window_y))
        self.pixel = pygame.Surface((self.x, self.y))


    def draw(self, image):
        
        for i in range(len(self.image)):
            if self.image[i] == 0:
                self.pixel.fill((0, 0, 0))
            else:
                self.pixel.fill((255, 255, 255))

    def clear(self):
        pass
