

class Bar:
    def __init__(self):
        self.date = 20010101
        self.open = 0.0
        self.high = 0.0
        self.low = 0.0
        self.close = 0.0
        self.volume = 0

class Stock:
    def __init__(self, text):
        self.bars = []
        for line in text.readlines():
            bar = Bar()
            words = line.split()
            bar.date = int(words[0].replace('/', ''))
            bar.open = float(words[1])
            bar.high = float(words[2])
            bar.low = float(words[3])
            bar.close = float(words[4])
            bar.volume = float(words[5])
            self.bars.append(bar)
