#!/usr/bin/python
### Lazy Generate Byte String
# for i in $(xxd -c 1 Particle\ Demo\ \[zeroZshadow\,\ 2008\].ch8 | cut -d ' ' -f 2); do echo -n "\x$i"; done; echo
import random
import os.path
from fontset import fonts as FONTS
from display import display as osdisplay

CH8_DISPLAY = 64 * 32
CH8_MEMORY = 4096
CH8_REGISTERS = 16
CH8_STACK = 16 * 2
CH8_INPUTS = 16

ch8_rom = b'\xa3\x21\x60\x00\x61\x00\x62\x08\xd0\x15\xf2\x1e\x80\x24\xd0\x15\xf2\x1e\x80\x24\xd0\x15\xf2\x1e\x80\x24\xd0\x15\xf2\x1e\x80\x24\xd0\x15\xf2\x1e\x80\x24\xd0\x15\xf2\x1e\x80\x24\xd0\x15\xf2\x1e\x80\x24\xd0\x15\x66\x05\x67\x02\x6a\x00\x12\xb8\x6b\x00\x6c\x00\xa2\xd8\xfb\x1e\xf3\x65\x22\xce\x22\x5c\x12\x62\x22\xce\x22\x5c\x7b\x04\x7c\x01\x5c\x60\x12\x40\x12\x3c\x12\x00\xa3\x20\xde\xd1\x00\xee\xa2\xd8\xfb\x1e\xf3\x65\x80\x24\x81\x34\x8e\x00\x8d\x10\x8e\xe6\x8d\xd6\x84\xe0\x65\xc2\x84\x54\x4f\x01\x12\x92\x4d\x00\x63\x01\x84\xd0\x65\xe1\x84\x54\x4f\x01\x12\x92\x33\x02\x73\x01\x12\x94\x22\x9c\xa2\xd8\xfb\x1e\xf3\x55\x12\x4c\xa3\x00\xfa\x1e\xf0\x65\x82\x00\x7a\x01\x64\x1f\x8a\x42\x60\x20\x61\x1e\x80\x0e\x81\x1e\xc3\x03\x73\xf8\x00\xee\x6b\x00\x6c\x00\x22\x9c\xa2\xd8\xfb\x1e\xf3\x55\x7b\x04\x7c\x01\x5c\x60\x12\xbc\x12\x3c\x8e\x00\x8d\x10\x8e\xe6\x8d\xd6\x00\xee\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xf8\xfa\xf9\xfe\xfb\xfc\xfd\xff\x02\x01\x03\x05\x04\x06\x07\x08\x06\x07\x04\x05\x03\x01\x02\xfe\xff\xfc\xfb\xfd\xfa\xf9\xf8\xfa\x80\xf7\x06\x77\x06\x36\x00\x00\x00\xc7\x6c\xcf\x0c\x0c\x00\x00\x00\x9f\xd9\xdf\xd9\xd9\x00\x00\x00\x3f\x8c\x0c\x8c\x8c\x00\x00\x00\x67\x6c\x6c\x6c\x67\x00\x00\x00\xb0\x30\x30\x30\xbe\x00\x00\x00\xf9\xc3\xf1\xc0\xfb\x00\x00\x00\xef\x00\xce\x60\xcc\x00\x00\x00'

if os.path.exists('rom.ch8'):
    with open("rom.ch8", "rb") as rom:
        ch8_rom = bytearray(rom.read())

class ch8():

    def __init__(self, rom):
        self.opcode = 0x0000
        self.pc = 0x200
        self.index = 0x000
        self.sp = 0x00
        self.memory = bytearray(CH8_MEMORY)
        self.registers = bytearray(CH8_REGISTERS)
        self.image = bytearray(CH8_DISPLAY)
        self.display = osdisplay(64, 32, 1024, 512)
        self.stack = bytearray(CH8_STACK)
        self.input = bytearray(CH8_INPUTS)
        self.draw = False
        self.timers = {
                    "delay": 0x0,
                    "sound": 0x0
                }

        self.op_lut = {
                    0x0: self.clear_disp,
                    0x1: self.jump_addr,
                    0x2: self.call_sub,
                    0x3: self.skip_next_if_eq,
                    0x4: self.skip_next_if_ne,
                    0x5: self.skip_next_if_eq_reg,
                    0x6: self.put_in_reg,
                    0x7: self.add_in_reg,
                    0x8: self.logical_ops,
                    0x9: self.skip_next_if_ne_reg,
                    0xA: self.set_index,
                    0xB: self.jump_add_v0,
                    0xC: self.and_with_rand,
                    0xD: self.disp_sprite,
                    0xE: self.process_key,
                    0xF: self.misfits,
                }

        self.logical_op_lut = {
                    0x0: self.set_eq_to,
                    0x1: self.x_or_y,
                    0x2: self.x_and_y,
                    0x3: self.x_xor_y,
                    0x4: self.x_add_y_carry,
                    0x5: self.x_sub_y,
                    0x6: self.div_by_two,
                    0x7: self.y_sub_x,
                    0xE: self.mult_by_two,
                }

        self.misfit_op_lut = {
                    0x07: self.get_delay_timer,
                    0x0A: self.wait_for_key,
                    0x15: self.set_delay_timer,
                    0x18: self.set_sound_timer,
                    0x1E: self.add_index,
                    0x29: self.set_index_to_font,
                    0x33: self.store_bcd,
                    0x55: self.write_reg_to_mem,
                    0x65: self.read_reg_from_mem,
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
        if self.opcode != 0:
            print(hex(self.opcode))
        
        try:
            self.op_lut[(self.opcode & 0xF000) >> 12]()
        except KeyError:
            print("Unknown Instruction")

        # Decrement timers by one each cycle to a minimum of 0
        self.timers = {i:max(j - 1, 0) for i,j in self.timers.items()}

        self.pc += 2

    def logical_ops(self):
        op = self.opcode & 0x000F
        self.logical_op_lut[op]()

    def misfits(self):
        op = self.opcode & 0x00FF
        self.misfit_op_lut[op]()

    def access_pixel(self, x, y, mode):
        # If mode == True, set pixel and return True for collision
        # If mode == False, return pixel

        bit_shift = (x % 8)
        byte = ((y * 64 + x) // 8)

        curr_value = (self.image[byte] >> bit_shift) & 0x01

        #print("shift: {} byte: {} curr_val: {}".format(bit_shift, byte, curr_value))

        if not mode:
            return curr_value
        else:
            self.image[byte] ^= (0x01 << bit_shift)
            if curr_value == 1:
                return 1
            else:
                return 0
    
    def clear_disp(self):
        """00E0 Clear the screen
        """
        if (self.opcode & 0x000F) == 0xE:
            self.pc = self.stack.pop()
            self.pc |= (self.stack.pop() << 8)
            return
        self.display.clear()
        self.draw = True

    def jump_addr(self):
        """1NNN Jump to address NNN
        """
        self.pc = self.opcode & 0x0FFF

    def call_sub(self):
        """2NNN Execute subroutine starting at address NNN
        """
        self.stack.append((self.pc & 0xFF00) >> 8)
        self.stack.append(self.pc & 0x00FF)
        self.pc = (self.opcode & 0x0FFF)
        self.sp += 2
    
    def skip_next_if_eq(self):
        """3XNN Skip the following instruction if the value of register VX equals NN
        """
        if (self.opcode & 0x00FF) == self.registers[(self.opcode & 0x0F00) >> 8]:
            self.pc += 2

        print("Is {} equal to {}?".format(hex(self.registers[(self.opcode & 0x0F00) >> 8]), hex(self.opcode & 0x00FF)))

    def skip_next_if_ne(self):
        """4XNN Skip the following instruction if the value of register VX is not equal to NN
        """
        if (self.opcode & 0x00FF) != self.registers[(self.opcode & 0x0F00) >> 8]:
            self.pc += 2

    def skip_next_if_eq_reg(self):
        """5XY0 Skip the following instruction if the value of register VX is equal to the value of register VY
        """
        if self.registers[(self.opcode & 0x0F00) >> 8] == self.registers[(self.opcode & 0x00F0) >> 4]:
            self.pc += 2

    def put_in_reg(self):
        """6XNN Store number NN in register VX
        """
        print("Storing {} in register {}".format(self.opcode & 0x00FF, (self.opcode & 0x0F00) >> 8))
        self.registers[(self.opcode & 0x0F00) >> 8] = self.opcode & 0x00FF
        print("V{}: {}".format((self.opcode & 0x0F00) >> 8, self.registers[(self.opcode & 0x0F00) >> 8]))

    def add_in_reg(self):
        """7XNN Add the value NN to register VX
        """
        vx = (self.opcode & 0x0F00) >> 8
        self.registers[vx] = self.registers[vx] + (self.opcode & 0x00FF) & 0xFF
        print("Add {} to {}".format((self.opcode & 0x00FF), self.registers[vx]))
        print(self.registers[vx])

    def skip_next_if_ne_reg(self):
        """9XY0 Skip the following instruction if the value of register VX is not equal to the value of register VY
        """
        if self.registers[(self.opcode & 0x0F00) >> 8] != self.registers[(self.opcode & 0x00F0) >> 4]:
            self.pc += 2

    def set_index(self):
        """ANNN Store memory address NNN in register I
        """
        self.index = self.opcode & 0x0FFF

    def jump_add_v0(self):
        """BNNN Jump to address NNN + V0
        """
        self.pc = (self.opcode & 0x0FFF) + self.registers[0]

    def and_with_rand(self):
        """CXNN Set VX to a random number with a mask of NN
        """
        val = (self.opcode & 0x0F00) >> 8
        self.registers[val] = self.registers[val] & random.randint(0,255)

    def disp_sprite(self):
        """DXYN Draw a sprite at position VX, VY with N bytes of sprite data starting at the address stored in I
        Set VF to 01 if any set pixels are changed to unset, and 00 otherwise
        """
        sprite_addr = self.index
        num_bytes = self.opcode & 0x000F
        xpos = self.registers[(self.opcode & 0x0F00) >> 8]
        ypos = self.registers[(self.opcode & 0x00F0) >> 4]

        sprite = self.memory[(sprite_addr):(sprite_addr + num_bytes)]

        for i in range(len(sprite)):
            for j in reversed(range(8)):
                pixel = (sprite[i] >> j) & 0x01
                if pixel == 1:
                    x = xpos + 8 - j 
                    y = ypos + i
                    self.registers[15] = self.access_pixel(x, y, True)
        
        self.draw = True

    def process_key(self):
        """EX9E Skip the following instruction if the key corresponding to the hex value currently stored in register VX is pressed
        EXA1    Skip the following instruction if the key corresponding to the hex value currently stored in register VX is not pressed

        """
        pass

    def set_eq_to(self):
        """8XY0 Store the value of register VY in register VX
        """
        self.registers[(self.opcode & 0x0F00) >> 8] = self.registers[(self.opcode & 0x00F0) >> 4]

    def x_or_y(self):
        """8XY1 Set VX to VX OR VY
        """
        self.registers[(self.opcode & 0x0F00) >> 8] |= self.registers[(self.opcode & 0x00F0) >> 4]

    def x_and_y(self):
        """8XY2 Set VX to VX AND VY
        """
        self.registers[(self.opcode & 0x0F00) >> 8] &= self.registers[(self.opcode & 0x00F0) >> 4]

    def x_xor_y(self):
        """8XY3 Set VX to VX XOR VY
        """
        self.registers[(self.opcode & 0x0F00) >> 8] ^= self.registers[(self.opcode & 0x00F0) >> 4]

    def x_add_y_carry(self):
        """8XY4 Add the value of register VY to register VX
        Set VF to 01 if a carry occurs
        Set VF to 00 if a carry does not occur
        """
        vx = (self.opcode & 0x0F00) >> 8
        vy = (self.opcode & 0x00F0) >> 4

        if (self.registers[vx] + self.registers[vy]) > 0xFF:
            self.registers[15] = 0x1
            self.registers[vx] = (self.registers[vx] + self.registers[vy]) & 0xFF
        else:
            self.registers[15] = 0x0
            self.registers[vx] += self.registers[vy]

    def x_sub_y(self):
        """8XY5 Subtract the value of register VY from register VX
        Set VF to 00 if a borrow occurs
        Set VF to 01 if a borrow does not occur
        """
        vx = (self.opcode & 0x0F00) >> 8
        vy = (self.opcode & 0x00F0) >> 4

        print(self.registers[vx], self.registers[vy])
        if self.registers[vx] < self.registers[vy]:
            self.registers[0xf] = 0x0
            self.registers[vx] = (self.registers[vx] - self.registers[vy]) & 0xFF
        else:
            self.registers[0xf] = 0x1
            self.registers[vx] = self.registers[vx] - self.registers[vy]

    def div_by_two(self):
        """8XY6 Store the value of register VX shifted right one bit in register VY¹
        Set register VF to the least significant bit prior to the shift
        """
        vx = self.registers[(self.opcode & 0x0F00) >> 8]

        self.registers[15] = vx & 0x1
        self.registers[(self.opcode & 0x00F0) >> 4] = (vx >> 1)

    def y_sub_x(self):
        """8XY7 Set register VX to the value of VY minus VX
        Set VF to 00 if a borrow occurs
        Set VF to 01 if a borrow does not occur
        """
        vx = (self.opcode & 0x0F00) >> 8
        vy = (self.opcode & 0x00F0) >> 4

        if self.registers[vy] < self.registers[vx]:
            self.registers[15] = 0x0
            self.registers[vx] = abs(self.registers[vy] - self.registers[vx]) & 0xFF
        else:
            self.registers[15] = 0x1
            self.registers[vx] = self.registers[vy] - self.registers[vx]

    def mult_by_two(self):
        """8XYE Store the value of register VX shifted left one bit in register VY¹
        Set register VF to the most significant bit prior to the shift
        """
        vx = self.registers[(self.opcode & 0x0F00) >> 8]

        self.registers[15] = (vx >> 7) & 0x1
        self.registers[(self.opcode & 0x00F0) >> 4] = (vx << 1) & 0xFF

    def get_delay_timer(self):
        """FX07 Store the current value of the delay timer in register VX
        """
        self.registers[(self.opcode & 0x0F00) >> 8] = self.timers['delay']

    def wait_for_key(self):
        """FX0A Wait for a keypress and store the result in register VX
        """
        pass

    def set_delay_timer(self):
        """FX15 Set the delay timer to the value of register VX
        """
        self.timers['delay'] = self.registers[(self.opcode & 0x0F00) >> 8]

    def set_sound_timer(self):
        """FX18 Set the sound timer to the value of register VX
        """
        self.timers['sound'] = self.registers[(self.opcode & 0x0F00) >> 8]

    def add_index(self):
        """FX1E Add the value stored in register VX to register I
        """
        self.index = (self.index + self.registers[(self.opcode & 0x0F00) >> 8]) & 0xFFF

    def set_index_to_font(self):
        """FX29 Set I to the memory address of the sprite data corresponding to the hexadecimal digit stored in register VX
        """
        byte_length = 0x05
        digit = (self.opcode & 0x0F00) >> 8
        self.index = 0x50 + (byte_length * digit)

    def store_bcd(self):
        """FX33 Store the binary-coded decimal equivalent of the value stored in register VX at addresses I, I + 1, and I + 2
        """
        vx = (self.opcode & 0x0F00) >> 8
        self.memory[self.index] = self.registers[vx] // 100
        self.memory[self.index + 1] = self.registers[vx] % 100 // 10
        self.memory[self.index + 2] = self.registers[vx] % 10


    def write_reg_to_mem(self):
        """FX55 Store the values of registers V0 to VX inclusive in memory starting at address I
        I is set to I + X + 1 after operation²
        """
        vx = (self.opcode & 0x0F00) >> 8
        print(self.index)
        for i in range(0, vx + 1):
            self.memory[self.index + i + 1] = self.registers[i]
            print(self.registers[i])
        self.index += ((self.opcode & 0x0F00) >> 8)
        for i in range(self.index - 10, self.index + 10):
            print(i, ":", self.memory[i])


    def read_reg_from_mem(self):
        """FX65 Fill registers V0 to VX inclusive with the values stored in memory starting at address I
        I is set to I + X + 1 after operation
        """
        vx = (self.opcode & 0x0F00) >> 8
        print(self.index)
        for i in range(0, ((self.opcode & 0x0F00) >> 8) + 1):
            self.registers[i] = self.memory[self.index + i]
            print("writing to reg", i, "with", self.memory[self.index + i])
        self.index += ((self.opcode & 0x0F00) >> 8) 
        for i in range(self.index - 10, self.index + 10):
            print(i, ":", self.memory[i])


if __name__ == "__main__":

    # Initialize ROM from source

    chate = ch8(ch8_rom)

    chate.display.debug = True

    while(True):

        input()

        if chate.display.debug and chate.display.state:
            state_dict = {
                        'pc': chate.pc,
                        'opcode': chate.opcode,
                        'registers': chate.registers,
                        'index': chate.index,
                        'sp': chate.sp,
                        'stack': chate.stack,
                        'mem_part': chate.memory[(chate.pc - 10):(chate.pc + 10)],
                    }
            
            chate.display.state = state_dict
            
        chate.cycle()
        if chate.draw:
            chate.display.draw(chate.image)
            chate.draw = False
        #chate.set_input()