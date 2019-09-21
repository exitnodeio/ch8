import pygame

class display:
    
    def __init__(self, x, y, win_x, win_y):
        self.x = x
        self.y = y

        self.window_x = win_x
        self.window_y = win_y

        self.screen = pygame.display.set_mode((self.window_x, self.window_y))
        self.surf = pygame.Surface((self.x, self.y))


    def draw(self, image):
        
        for i in range(len(image)):
            color = image[i] & 0x0001
            print(color)
            self.surf.set_at((i % self.x, i // self.y), color)

        self.blit_surf()
     
    def clear(self):
        self.surf.fill((0,0,0))
        self.blit_surf()

    def blit_surf(self):
        self.screen.blit(pygame.transform.scale(self.surf, (self.window_x, self.window_y)), (0,0))
