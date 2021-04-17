import pygame
import time

class display(object):
    
    def __init__(self, x, y, win_x, win_y, debug=False):
        self.x = x
        self.y = y

        self.window_x = win_x
        self.window_y = win_y
        
        self.COLOR_LUT = {
                    0: (0,0,0),
                    1: (255,255,255),
                    2: (15,22,69),
                    3: (179,187,255),
                }

        self.bytes_per_frame = int(self.x * self.y / 8)
        self.screen = pygame.display.set_mode((self.window_x, self.window_y))
        self.surf = pygame.Surface((self.x, self.y))

        self.depressed_keys = list()

    def poll_keys(self):
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.KEYDOWN:
                self.depressed_keys.append(event.key)
            if event.type == pygame.KEYUP:
                self.depressed_keys.remove(event.key)
        return depressed_keys

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
            self.surf.set_at(loc, self.COLOR_LUT[color])

        self.blit_surf()
     
    def clear(self):
        self.surf.fill(self.COLOR_LUT[0])
        self.blit_surf()

    def blit_surf(self):
        self.screen.blit(pygame.transform.scale(self.surf, (self.window_x, self.window_y)), (0, 0))
        pygame.display.flip()

class debug_display(display):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.state = dict()

        # Set emu display to 2/3rd's of window
        self.emu_display_x = int(self.window_x * ( 2 / 3 ))
        self.emu_display_y = int(self.window_y * ( 2 / 3 ))

        # Debug display dimensions
        self.reg_x = 0
        self.reg_y = self.emu_display_y
        self.reg_w = self.window_x
        self.reg_h = self.window_y - self.emu_display_y
        self.register_surface = False
        self.mem_x = self.emu_display_x
        self.mem_y = 0
        self.mem_w = self.window_x - self.emu_display_x
        self.mem_h = self.window_y
        self.memory_surface = False
        self.debug_surf = pygame.Surface((self.window_x, self.window_y))
        
        # PyGame font initialization
        pygame.font.init()
        self.font = pygame.font.Font('scp.ttf', 64)
        self.mem_title_font = pygame.font.Font('scp.ttf', 48)
        self.FONT_SPACING = 3
        self.title = self.font.render("CURRENT MEMORY POSITION", True, self.COLOR_LUT[3])
        self.font_padding = self.title.get_height() / self.FONT_SPACING

        # Bounds update timer
        self.last_bounds_update = 0 
        self.BOUNDS_DELAY = 6

        

        # Memory window initialization

    
    def draw(self, *args, **kwargs):
        self.debug_surf.fill(self.COLOR_LUT[2])
        self.draw_memory()
        self.last_bounds_update, self.memory_surface = self.update_bounds(self.last_bounds_update)
        super().draw(*args, **kwargs)

    def blit_surf(self, *args, **kwargs):
        self.screen.blit(self.debug_surf, (0, 0))
        super().blit_surf(*args, **kwargs)


    def update_bounds(self, last_time=0, *args, **kwargs):
        expiry = (time.time() - self.BOUNDS_DELAY)
        if self.last_bounds_update <= expiry:
            self.memory_bounds_width = self.font_padding
            self.memory_bounds_height = int(self.font_padding * 2 + self.title.get_height())
            for loc in self.mem_dict:
                self.memory_bounds_height += self.mem_dict[loc]['text_obj'].get_height()
                font_width = self.mem_dict[loc]['text_obj'].get_width()
                if font_width > self.memory_bounds_width:
                    self.memory_bounds_width = font_width + self.font_padding * 2
            return (time.time(), pygame.Surface((self.memory_bounds_width, self.memory_bounds_height)))
        else:
            return (self.last_bounds_update, pygame.Surface((self.memory_bounds_width, self.memory_bounds_height)))

#            text_list = list()
#            surf_height = 0
#            surf_width = 0
#            height_spacing = int(text_list[0].get_height() / self.FONT_SPACING)
#            surf_height += height_spacing * (len(text_list) + 1)
#            surf_width += (height_spacing * 2)
#            top_spacing = height_spacing + self.title.get_height()
#            self.last_bounds_update = update_bounds(last_time=last_update)
#
#            return (time.time(), (self.memory_bounds_width, self.memory_bounds_height))

    def draw_memory(self):

        memory_x = self.font_padding
        memory_y = self.font_padding * 2 + self.title.get_height()

        self.mem_dict = self.state['memory'].copy()
        for loc in self.mem_dict.keys():
            self.mem_dict.update({loc: {}})
            self.mem_dict[loc].update({ 'value': loc })
            self.mem_dict[loc].update({ 'offset': loc - self.state['pc'] })
            self.mem_dict[loc].update({ 'hex': "{:02x}".format(self.state['memory'][loc]).upper()})
            self.mem_dict[loc].update({ 'binary': "{:08b}".format(self.state['memory'][loc])})
            self.mem_dict[loc].update({ 'text_obj': self.font.render("{}  :  {}  :  {}/{} ".format( \
                    str(self.mem_dict[loc]['offset']).rjust(3), \
                    "{:04x}".format(self.mem_dict[loc]['value']).upper(), \
                    self.mem_dict[loc]['hex'], \
                    self.mem_dict[loc]['binary']), True, self.COLOR_LUT[3]) })
            
            if self.memory_surface:
                self.memory_surface.blit(self.mem_dict[loc]['text_obj'], (memory_x, memory_y))
                memory_y += self.mem_dict[loc]['text_obj'].get_height()
        if self.memory_surface and self.debug_surf:        
            self.memory_surface = pygame.transform.scale(self.memory_surface, (int((self.mem_h / self.memory_surface.get_height()) * self.memory_surface.get_width()), self.mem_h))
            self.debug_surf.blit(self.memory_surface, (self.emu_display_x, 0))
        #text_surf.blit(self.title, (text_surf.get_width() - (self.title.get_width() // 2), 0))
        #text_surf = pygame.transform.scale(text_surf, (self.mem_w, int((self.mem_w / text_surf.get_width()) * text_surf.get_height())))
        
    def draw_registers(self):
        pass 
