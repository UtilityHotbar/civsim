import blessed
import textwrap


class Frame:
    def __init__(self, term,  start_x, start_y, width, height, frame=' '):
        self.term = term
        self.start_x = start_x
        self.start_y = start_y
        self.width = width
        self.height = height
        self.frame = frame
        self.cy = 0
        self.content = []
        self.focused = False

    def clear(self):
        data = self.content
        self.content = []
        return data

    def push(self, *args):
        for arg in args:
            self.content.append(arg)

    def display(self, bottom=False, dynamic_height=True, centered=False):
        displayContent = []
        for line in self.content:
            long_arg = line.split('\n')
            for subarg in long_arg:
                displayContent += textwrap.wrap(subarg, self.width - 2)
        if bottom:
            displayContent = list(reversed(list(reversed(displayContent))[:min(self.height-2, len(displayContent))]))
        if not dynamic_height and len(displayContent) < self.height - 2:
            displayContent += ['']*((self.height-2)-len(displayContent))

        curr = 0
        with self.term.location(self.start_x, self.start_y):
            print(self.frame*self.width)
        for i in range(self.height-2):
            curr_content = displayContent[curr]
            with self.term.location(self.start_x, self.start_y + self.cy + 1):
                if centered:
                    half = int((self.width - 2 - len(curr_content))/2)
                    print(self.frame +
                          ' ' * half +
                          curr_content +
                          ' ' * (half+(self.width-2-len(curr_content)-2*half)) +
                          self.frame)
                else:
                    print(self.frame +
                          curr_content +
                          ' '*(self.width-2-len(curr_content)) +
                          self.frame)
            curr += 1
            self.cy += 1
            if curr > len(displayContent)-1:
                break
        with self.term.location(self.start_x, self.start_y + curr + 1):
            print(self.frame * self.width)

    def __len__(self):
        return len(self.content)



if __name__ == '__main__':
    term = blessed.Terminal()
    with term.fullscreen():
        while True:
            myFrame = Frame(term, 1, 1, 20, 10, frame='~')
            myFrame.content.append('CHRIS\' CHARACTER SHEET\nName: Albert\nClass: Wizard\nStr: 10\nDex: 05\nCha: 19')
            myFrame.display(dynamic_height=False, centered=True)
            print(term.move_y(term.height-1), 'test')
            i = input(' testinput> ')
            if i == 'q':
                break
    print(term.clear())
