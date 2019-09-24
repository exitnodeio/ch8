import pygame

class display():
    
    def __init__(self, x, y, win_x, win_y):
        self.x = x
        self.y = y

        self.window_x = win_x
        self.window_y = win_y
        self.bytes_per_frame = int(self.x * self.y / 8)

        self.state = {
                'pc':'',
                'op':'',
                'registers':'',
                'index':'',
                'sp':'',
                'stack':'',
                'mem_part':'',
                }

        self.screen = pygame.display.set_mode((self.window_x, self.window_y))
        self.surf = pygame.Surface((self.x, self.y))

        self.color_lut = {
                    0: (0,0,0),
                    1: (255,255,255),
                }

    def access_bit(self, data, num):
        base = int(num // 8)
        shift = int(num % 8)
        return (data[base] & (1<<shift)) >> shift

    def draw(self, image):

        if len(image) < self.bytes_per_frame:
            image += b'\x00' * self.bytes_per_frame

        for i in range(self.x * self.y):
            color = self.access_bit(image, i)
            loc = (i % self.x, i // self.x)
            self.surf.set_at(loc, self.color_lut[color])

        self.blit_surf()
     
    def clear(self):
        self.surf.fill((0,0,0))
        self.blit_surf()

    def blit_surf(self):
        self.screen.blit(pygame.transform.scale(self.surf, (self.window_x, self.window_y)), (0,0))
        pygame.display.flip()

