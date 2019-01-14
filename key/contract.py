#!/usr/bin/python

class Bar:
    def __init__(self):
        self.date = 20010101
        self.time = 0.0901
        self.open = 0.0
        self.high = 0.0
        self.low = 0.0
        self.close = 0.0
        self.volume = 0
        self.openInterest = 0
        self.settlement = 0


class Contract:
    def __init__(self, name, text):
        self.name = name
        self.bars = []
        for line in text.readlines():
            bar = Bar()
            words = line.split()
            bar.date = int(words[0].replace('/', ''))
            bar.time = float('0.' + words[1])
            bar.open = float(words[2])
            bar.high = float(words[3])
            bar.low = float(words[4])
            bar.close = float(words[5])
            bar.volume = float(words[6])
            bar.openInterest = float(words[7])
            bar.settlement = float(words[8])
            self.bars.append(bar)


