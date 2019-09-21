from fontset import fonts as FONTS
from display import display as osdisplay

CH8_DISPLAY = 64 * 32
CH8_MEMORY = 4096
CH8_REGISTERS = 16
CH8_STACK = 16
CH8_INPUTS = 16

ch8_rom = 0

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

        if rom == 0:
            print("ROM Data is Empty.  Bye Bye.")
            quit()

        # Load Fontset into Memory
        for i in range(len(FONTS)):
            memory[i + 0x50] = FONTS[i]
        
        # Load ROM into Memory
        for i in range(len(rom)):
            memory[i + pc] = rom[i]

    def cycle(self):
        # Assign opcode by shifting first byte left by 8 bits, and assigning the second byte to the 8 LSBs.
        opcode = memory[pc] << 8 | memory[pc + 1]


    def set_input(self):
        self.input

if __name__ == "__main__":
    
    # Initialize ROM from source

    chate = ch8(ch8_rom)

    while(True):


        chate.cycle()
        if chate.draw:
            chate.display.draw(chate.image)
        chate.set_input()
