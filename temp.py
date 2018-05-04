class ScreenBuilder(object):
    def __init__(self, x, y):
        super(ScreenBuilder, self).__init__()
        self.x = x
        self.y = y
        self.corner_char = '└'
        self.vertical_char = '│'
        self.horizontal_char = '─'
        self.matrix = ["asdsads", "adasdas"]
        self.resize()

    def enlarge_h(self):
        self.x += 1
        self.resize()

    def shrink_h(self):
        self.x -= 1
        self.resize()

    def enlarge_v(self):
        self.y += 1
        self.resize()

    def shrink_v(self):
        self.y -= 1
        self.resize()

    def resize(self):
        self.matrix = ''
        for n in range(0, self.y):
            self.matrix += f'{self.vertical_char}\n'
        self.matrix += f'{self.corner_char}{self.x * self.horizontal_char}'

    def get_screen(self):
        out = f'{self.x * self.horizontal_char}'
        offset = 0
        for y in self.y:
            while self.matrix[-1 * y - offset] > self.x:
                offset += 1
            line = self.matrix[-1 * y - offset]
            while line > self.x:
                n_lines = len(line) /

                out = f'{}\n{out}'

    def write_line(self, text, line=0):
        lines = self.matrix.split('\n')
        lines[line] = f'{self.vertical_char} {text}'
        self.matrix = '\n'.join(lines)
