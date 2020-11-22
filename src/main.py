# By Oscar MacKenzie (https://github.com/oscarmac384)

# NOTE: THIS PROGRAM ONLY WORKS ON WINDOWS
# USAGE: python main.py <path to ROM>


import time
import random
import sys

import components


class Chip8Emulator:
    """The main class for the emulator,
    handles CPU functions including opcodes"""

    def __init__(self, rom_name):
        self.window = components.Display()

        self.keyboard = components.Keyboard()
        self.speaker = components.Speaker()

        self.memory = [0]*4096
        self.v = [0]*16
        self.i = 0
        self.pc = 0x200
        self.stack = []

        self.delay_timer = 0
        self.sound_timer = 0

        self.speed = 10
        self.paused = False
        self.fps = 60

        self.load_sprites_into_memory()
        self.load_rom(rom_name)
        self.game_loop()

    def load_sprites_into_memory(self):
        """Load the predefined CHIP-8 sprites into memory"""

        sprites = [
            0xF0, 0x90, 0x90, 0x90, 0xF0, # 0
            0x20, 0x60, 0x20, 0x20, 0x70, # 1
            0xF0, 0x10, 0xF0, 0x80, 0xF0, # 2
            0xF0, 0x10, 0xF0, 0x10, 0xF0, # 3
            0x90, 0x90, 0xF0, 0x10, 0x10, # 4
            0xF0, 0x80, 0xF0, 0x10, 0xF0, # 5
            0xF0, 0x80, 0xF0, 0x90, 0xF0, # 6
            0xF0, 0x10, 0x20, 0x40, 0x40, # 7
            0xF0, 0x90, 0xF0, 0x90, 0xF0, # 8
            0xF0, 0x90, 0xF0, 0x10, 0xF0, # 9
            0xF0, 0x90, 0xF0, 0x90, 0x90, # A
            0xE0, 0x90, 0xE0, 0x90, 0xE0, # B
            0xF0, 0x80, 0x80, 0x80, 0xF0, # C
            0xE0, 0x90, 0x90, 0x90, 0xE0, # D
            0xF0, 0x80, 0xF0, 0x80, 0xF0, # E
            0xF0, 0x80, 0xF0, 0x80, 0x80  # F
        ]

        for i in range(len(sprites)):
            self.memory[i] = sprites[i]

    def load_program_into_memory(self, program):
        """Load the program into memory, starting at 0x200"""

        for loc in range(len(program)):
            self.memory[0x200 + loc] = program[loc]

    def load_rom(self, rom_name):
        """Reads the rom in binary mode and calls the function to load it into memory"""

        with open(rom_name, 'rb') as f:
            program = f.read()
            self.load_program_into_memory(program)

    def update_timers(self):
        """Updates the delay and sound timer of the program"""

        if self.delay_timer > 0:
            self.delay_timer -= 1
        if self.sound_timer > 0:
            self.sound_timer -= 1

    def play_sound(self):
        """Plays a beep sound when the sound timer is greater than zero"""

        if self.sound_timer > 0:
            self.speaker.play()

    def execute_instruction(self, opcode):
        """Executes all the opcodes for the CHIP-8 CPU"""

        self.pc += 2

        x = (opcode & 0x0F00) >> 8
        y = (opcode & 0x00F0) >> 4

        # All the opcodes
        c = opcode & 0xF000
        if c == 0x0000:
            if opcode == 0x00E0:
                self.window.clear()

            elif opcode == 0x00EE:
                self.pc = self.stack.pop()

        elif c == 0x1000:
            self.pc = (opcode & 0xFFF)

        elif c == 0x2000:
            self.stack.append(self.pc)
            self.pc = (opcode & 0xFFF)

        elif c == 0x3000:
            if self.v[x] == (opcode & 0xFF):
                self.pc += 2

        elif c == 0x4000:
            if self.v[x] != (opcode & 0xFF):
                self.pc += 2

        elif c == 0x5000:
            if self.v[x] == self.v[y]:
                self.pc += 2

        elif c == 0x6000:
            self.v[x] = (opcode & 0xFF)

        elif c == 0x7000:
            self.v[x] += (opcode & 0xFF)

        elif c == 0x8000:
            sub_c = opcode & 0xF
            if sub_c == 0x0:
                self.v[x] = self.v[y]

            elif sub_c == 0x1:
                self.v[x] |= self.v[y]

            elif sub_c == 0x2:
                self.v[x] &= self.v[y]

            elif sub_c == 0x3:
                self.v[x] ^= self.v[y]

            elif sub_c == 0x4:
                xy_sum = self.v[x] + self.v[y]
                self.v[x] += self.v[y]
                self.v[0xF] = 0

                if xy_sum > 0xFF:
                    self.v[0xF] = 1
                self.v[x] = xy_sum

            elif sub_c == 0x5:
                self.v[0xF] = 0

                if self.v[x] > self.v[y]:
                    self.v[0xF] = 1
                self.v[x] -= self.v[y]

            elif sub_c == 0x6:
                self.v[0xF] = (self.v[x] & 0x1)
                self.v[x] >>= 1

            elif sub_c == 0x7:
                self.v[0xF] = 0

                if self.v[y] > self.v[x]:
                    self.v[0xF] = 1
                self.v[x] = self.v[y] - self.v[x]

            elif sub_c == 0xE:
                self.v[0xF] = (self.v[x] & 0x80)
                self.v[x] <<= 1

        elif c == 0x9000:
            if self.v[x] != self.v[y]:
                self.pc += 2

        elif c == 0xA000:
            self.i = (opcode & 0xFFF)

        elif c == 0xB000:
            self.pc = (opcode & 0xFFF) + self.v[0]

        elif c == 0xC000:
            self.v[x] = random.randint(0, 0xFF) & (opcode & 0xFF)

        elif c == 0xD000:
            width = 8
            height = (opcode & 0xF)
            self.v[0xF] = 0

            for row in range(height):
                sprite = self.memory[self.i + row]

                for col in range(width):
                    if (sprite & 0x80) > 0:
                        if self.window.set_pixel(self.v[x] + col, self.v[y] + row):
                            self.v[0xF] = 1
                    sprite <<= 1

        elif c == 0xE000:
            sub_c = opcode & 0xFF
            if sub_c == 0x9E:
                if self.v[x] in self.keyboard.keys_pressed:
                    self.pc += 2

            elif sub_c == 0xA1:
                if self.v[x] not in self.keyboard.keys_pressed:
                    self.pc += 2

        elif c == 0xF000:
            sub_c = opcode & 0xFF
            if sub_c == 0x07:
                self.v[x] = self.delay_timer

            elif sub_c == 0x0a:
                self.paused = True
                prev_keys = self.keyboard.keys_pressed

                while True:
                    self.keyboard.read_input()
                    if self.keyboard.keys_pressed != prev_keys:
                        self.v[x] = list(set(self.keyboard.keys_pressed) ^ set(prev_keys))[0]
                        self.paused = False
                        break

                    prev_keys = self.keyboard.keys_pressed

            elif sub_c == 0x15:
                self.delay_timer = self.v[x]

            elif sub_c == 0x18:
                self.sound_timer = self.v[x]

            elif sub_c == 0x1E:
                self.i += self.v[x]

            elif sub_c == 0x29:
                self.i = self.v[x] * 5

            elif sub_c == 0x33:
                self.memory[self.i] = self.v[x] // 100
                self.memory[self.i+1] = (self.v[x] % 100) // 10
                self.memory[self.i+2] = self.v[x] % 10

            elif sub_c == 0x55:
                for register_index in range(x+1):
                    self.memory[self.i + register_index] = self.v[register_index]

            elif sub_c == 0x65:
                for register_index in range(x+1):
                    self.v[register_index] = self.memory[self.i + register_index]
        else:
            raise Exception(f'Unkown opcode: {opcode}')

        self.v[x] %= 256

    def cycle(self):
        """Executes a cycle which will render the display,
        execute opcodes and play any sounds"""

        for _ in range(self.speed):
            if not self.paused:
                opcode = (self.memory[self.pc] << 8 | self.memory[self.pc + 1])
                self.execute_instruction(opcode)

        if not self.paused:
            self.update_timers()

        self.play_sound()
        self.window.render_display()

    def game_loop(self):
        """The main game loop,
        reads keyboard input and runs a cycle 60 times per second"""

        while not self.paused:
            start = time.time()

            self.keyboard.read_input()
            self.cycle()

            time.sleep(max(1/self.fps - (time.time() - start), 0))


if __name__ == '__main__':
    emulator = Chip8Emulator(sys.argv[1])
