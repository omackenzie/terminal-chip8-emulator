import winsound

import win32console, win32con, win32api
import pywintypes


class Display:
    """Outputs the display from the emulator into the terminal
    Uses win32console functions for increased efficiency"""

    def __init__(self):
        self.cols = 64
        self.rows = 32
        self.display_arr = [[0]*self.cols for _ in range(self.rows)]

        self.console_buffer = win32console.CreateConsoleScreenBuffer(
            DesiredAccess = win32con.GENERIC_READ | win32con.GENERIC_WRITE,
            ShareMode=0, SecurityAttributes=None, Flags=1)

        self.set_window_size()
        self.console_buffer.SetConsoleActiveScreenBuffer()

    def set_window_size(self):
        """Sets the window and buffer size of the console"""

        try:
            window_size = self.console_buffer.GetConsoleScreenBufferInfo()['Window']
            coord = win32console.PyCOORDType(X = (self.cols*2), Y = self.rows)
            self.console_buffer.SetConsoleScreenBufferSize(coord)

            window_size.Right = (self.cols*2) - 1
            window_size.Bottom = self.rows - 1

            self.console_buffer.SetConsoleWindowInfo(
                Absolute=True, ConsoleWindow=window_size)
        except pywintypes.error:
            raise Exception('Some issue occured when resizing the console, '
                'try decreasing the size or setting it back to default')

    def render_display(self):
        """Converts the display array into a string and
        outputs it to the screen"""

        write_string = ''
        for row in self.display_arr:
            for pixel in row:
                if pixel == 1:
                    write_string += '██'
                else:
                    write_string += '  '

        self.console_buffer.WriteConsoleOutputCharacter(
            write_string, win32console.PyCOORDType(0, 0))

    def set_pixel(self, x, y):
        """Sets a pixel on the display at a given position"""

        x %= self.cols
        y %= self.rows

        self.display_arr[y][x] ^= 1

        return not self.display_arr[y][x]

    def clear(self):
        """Resets the display array"""
        self.display_arr = [[0]*self.cols for _ in range(self.rows)]


class Keyboard:
    """Records any key presses and
    saves them to a list to be accessed by the emulator"""

    def __init__(self):
        self.keys_pressed = []
        self.on_next_key_press = None

    def read_input(self):
        """Records any keys pressed
        using the win32api GetAsyncKeyState function"""

        self.keys_pressed = []

        # 1
        if win32api.GetAsyncKeyState(0x31):
            self.keys_pressed.append(0x1)
        # 2
        if win32api.GetAsyncKeyState(0x32):
            self.keys_pressed.append(0x2)
        # 3
        if win32api.GetAsyncKeyState(0x33):
            self.keys_pressed.append(0x3)
        # 4
        if win32api.GetAsyncKeyState(0x34):
            self.keys_pressed.append(0xc)
        # Q
        if win32api.GetAsyncKeyState(0x51):
            self.keys_pressed.append(0x4)
        # W
        if win32api.GetAsyncKeyState(0x57):
            self.keys_pressed.append(0x5)
        # E
        if win32api.GetAsyncKeyState(0x45):
            self.keys_pressed.append(0x6)
        # R
        if win32api.GetAsyncKeyState(0x52):
            self.keys_pressed.append(0xD)
        # A
        if win32api.GetAsyncKeyState(0x41):
            self.keys_pressed.append(0x7)
        # S
        if win32api.GetAsyncKeyState(0x53):
            self.keys_pressed.append(0x8)
        # D
        if win32api.GetAsyncKeyState(0x44):
            self.keys_pressed.append(0x9)
        # F
        if win32api.GetAsyncKeyState(0x45):
            self.keys_pressed.append(0xE)
        # Z
        if win32api.GetAsyncKeyState(0x5A):
            self.keys_pressed.append(0xA)
        # X
        if win32api.GetAsyncKeyState(0x58):
            self.keys_pressed.append(0x0)
        # C
        if win32api.GetAsyncKeyState(0x43):
            self.keys_pressed.append(0xB)
        # V
        if win32api.GetAsyncKeyState(0x56):
            self.keys_pressed.append(0xF)


class Speaker:
    """Plays a beep sound when requested by the program
    The CHIP-8 can only produce one sound"""

    def __init__(self):
        self.sound_file = '../Sound/Beep.wav'

    def play(self):
        """Plays a beep sound in async"""

        winsound.PlaySound(self.sound_file, winsound.SND_ASYNC)
