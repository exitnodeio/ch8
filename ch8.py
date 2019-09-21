from fontset import fonts as FONTS
from display import display as osdisplay

CH8_DISPLAY = 64 * 32
CH8_MEMORY = 4096
CH8_REGISTERS = 16
CH8_STACK = 16
CH8_INPUTS = 16

ch8_rom = b'\x00\xe0\x63\x00\x64\x01\x65\xee\x35\xee\x13\x10\x63\x00\x64\x02\x65\xee\x66\xee\x55\x60\x13\x10\x63\x00\x64\x03\x65\xee\x45\xfd\x13\x10\x63\x00\x64\x04\x65\xee\x75\x01\x35\xef\x13\x10\x63\x00\x64\x05\x6f\x01\x65\xee\x66\xef\x85\x65\x3f\x00\x13\x10\x63\x00\x64\x06\x6f\x00\x65\xef\x66\xee\x85\x65\x3f\x01\x13\x10\x6f\x00\x63\x00\x64\x07\x65\xee\x66\xef\x85\x67\x3f\x01\x13\x10\x63\x00\x64\x08\x6f\x01\x65\xef\x66\xee\x85\x67\x3f\x00\x13\x10\x63\x00\x64\x09\x65\xf0\x66\x0f\x85\x61\x35\xff\x13\x10\x63\x01\x64\x00\x65\xf0\x66\x0f\x85\x62\x35\x00\x13\x10\x63\x01\x64\x01\x65\xf0\x66\x0f\x85\x63\x35\xff\x13\x10\x6f\x00\x63\x01\x64\x02\x65\x81\x85\x0e\x3f\x01\x13\x10\x63\x01\x64\x03\x6f\x01\x65\x47\x85\x0e\x3f\x00\x13\x10\x63\x01\x64\x04\x6f\x00\x65\x01\x85\x06\x3f\x01\x13\x10\x63\x01\x64\x05\x6f\x01\x65\x02\x85\x06\x3f\x00\x13\x10\x63\x01\x64\x06\x60\x15\x61\x78\xa3\xd0\xf1\x55\xf1\x65\x30\x15\x13\x10\x31\x78\x13\x10\x63\x01\x64\x07\x60\x8a\xa3\xd0\xf0\x33\xa3\xd0\xf0\x65\x30\x01\x13\x10\x60\x01\xf0\x1e\xf0\x65\x30\x03\x13\x10\x60\x01\xf0\x1e\xf0\x65\x30\x08\x13\x10\x13\x32\x13\x0e\xa3\x2a\x60\x13\x61\x09\xd0\x18\xf3\x29\x60\x22\x61\x0b\xd0\x15\xf4\x29\x60\x28\x61\x0b\xd0\x15\x13\x0e\xff\xf0\xf0\xff\xf0\xf0\xf0\xff\xa3\x58\x60\x15\x61\x0b\x63\x08\xd0\x18\x70\x08\xf3\x1e\x30\x2d\x13\x3a\xa3\x70\x60\x02\x61\x18\x63\x08\xd0\x18\x70\x05\xf3\x1e\x30\x3e\x13\x4c\x13\x0e\xf0\x88\x88\xf0\x88\x88\x88\xf0\x78\x84\x84\x84\x84\x84\x84\x78\x84\xc4\xa4\x94\x8c\x84\x84\x84\xc0\xa0\xa0\xc0\xa0\xa0\xc0\x00\x00\x00\xa0\xa0\xe0\x20\x20\xe0\x00\x00\x00\x00\x00\x00\x00\x00\xc0\xa0\xa0\xc0\xa0\xa0\xc0\x00\x00\x00\x60\xa0\xc0\x80\x60\x00\x00\x00\x60\x80\x40\x20\xc0\x00\x80\x80\xc0\x80\x80\x80\x60\x00\xe0\x80\x80\x80\x80\x80\xe0\x00\x00\x00\x40\xa0\xa0\xa0\x40\x00\x20\x20\x20\x60\xa0\xa0\x60\x00\x00\x00\x60\xa0\xc0\x80\x60\x00\x00\x00\x00\x60\x40\x40\x50\x00\x00\x00\x00\x00\x00\x00'

class ch8():

    def __init__(self, rom):
        self.opcode = 0x00
        self.pc = 0x200
        self.index = 0x00
        self.sp = 0x00
        self.memory = bytearray(CH8_MEMORY)
        self.registers = bytearray(CH8_REGISTERS)
        self.image = bytearray(CH8_DISPLAY)
        self.display = osdisplay(64, 32)
        self.stack = bytearray(CH8_STACK)
        self.input = bytearray(CH8_INPUTS)
        self.timers = {
                    "delay": 0x0,
                    "sound": 0x0
                }
        self.draw = False

        self.op_lut = {
                    0x0: self.clear_disp,
                    0x1: self.jump_addr,
                    0x2: self.call_sub,
                    0x3: self.skip_next_if_eq,
                    0x4: self.skip_next_if_ne,
                    0x5: self.skip_next_if_eq_reg,
                  #  0x6: self.put_in_reg,
                  #  0x7: self.add_in_reg,
                  #  0x8: self.logical_ops,
                  #  0x9: self.skip_next_if_ne_reg,
                  #  0xA: self.set_index,
                  #  0xB: self.jump_add_v0,
                  #  0xC: self.and_with_rand,
                  #  0xD: self.disp_sprite,
                  #  0xE: self.process_key,
                  #  0xF: self.misfits,
                }

        self.logical_op_lut = {
                  #  0x0: self.set_eq_to,
                  #  0x1: self.x_or_y,
                  #  0x2: self.x_and_y,
                  #  0x3: self.x_xor_y,
                  #  0x4: self.x_add_y_carry,
                  #  0x5: self.x_sub_y,
                  #  0x6: self.div_by_two,
                  #  0x7: self.y_sub_x,
                  #  0xE: self.mult_by_two,
                }

        self.misfit_op_lut = {
                  #  0x07: self.get_delay_timer,
                  #  0x0A: self.wait_for_key,
                  #  0x15: self.set_delay_timer,
                  #  0x18: self.set_sound_timer,
                  #  0x1E: self.add_index,
                  #  0x29: self.set_index_to_font,
                  #  0x33: self.store_bcd,
                  #  0x55: self.write_reg_to_mem,
                  #  0x65: self.read_reg_from_mem,
                }

        if rom == 0:
            print("ROM Data is Empty.  Bye Bye.")
            quit()

        # Load Fontset into Memory
        for i in range(len(FONTS)):
            self.memory[i + 0x50] = FONTS[i]
        
        # Load ROM into Memory
        for i in range(len(rom)):
            self.memory[i + self.pc] = rom[i]

    def cycle(self):
        # Assign opcode by shifting first byte left by 8 bits, and assigning the second byte to the 8 LSBs.
        self.opcode = self.memory[self.pc] << 8 | self.memory[self.pc + 1]

    def logical_ops(self):
        op = self.opcode & 0x000F
        self.logical_op_lut[op]()

    def misfits(self):
        op = self.opcode & 0x00FF
        self.misfit_op_lut[op]()

    def clear_disp(self):
        self.display.clear()

    def jump_addr(self):
        self.pc = self.opcode & 0x0FFF

    def call_sub(self):
        self.stack.append(self.pc)
        self.sp = len(self.stack)
    
    def skip_next_if_eq(self):
        if (self.opcode & 0x00FF) == self.registers[self.opcode & 0x0F00 >> 2]:
            self.pc += 2

    def skip_next_if_ne(self):
        if (self.opcode & 0x00FF) != self.registers[self.opcode & 0x0F00 >> 2]:
            self.pc += 2

    def skip_next_if_eq_reg(self):
        if self.registers[self.opcode & 0x0F00 >> 2] == self.registers[self.opcode & 0x00F0 >> 1]:
            self.pc += 2

    def put_in_reg:
        pass

    def add_in_reg:
        pass

    def logical_ops:
        pass

    def skip_next_if_ne_reg:
        pass

    def set_index:
        pass

    def jump_add_v0:
        pass

    def and_with_rand:
        pass

    def disp_sprite:
        pass

    def process_key:
        pass

    def misfits:
        pass

    def set_eq_to:
        pass

    def x_or_y:
        pass

    def x_and_y:
        pass

    def x_xor_y:
        pass

    def x_add_y_carry:
        pass

    def x_sub_y:
        pass

    def div_by_two:
        pass

    def y_sub_x:
        pass

    def mult_by_two:
        pass

    def get_delay_timer:
        pass

    def wait_for_key:
        pass

    def set_delay_timer:
        pass

    def set_sound_timer:
        pass

    def add_index:
        pass

    def set_index_to_font:
        pass

    def store_bcd:
        pass

    def write_reg_to_mem:
        pass

    def read_reg_from_mem:
        pass


if __name__ == "__main__":
    
    # Initialize ROM from source

    chate = ch8(ch8_rom)

    while(True):


        chate.cycle()
        if chate.draw:
            chate.display.draw(chate.image)
        #chate.set_input()
